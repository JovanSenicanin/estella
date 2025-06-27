from flask import Flask, render_template, request, jsonify
from langchain_openai import ChatOpenAI 
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
import os
import socket
import subprocess
import platform

# Load OpenAI API key from environment
openai_api_key = os.getenv("OPENAI_API_KEY")

# If running locally without env, fallback
if not openai_api_key:
    openai_api_key = "sk-proj-b199YOxjL0CxWM11ozg2T3BlbkFJidoS82AtjQkjzIVmBwY7"  # Optional: use for local testing

# Read the prompt from the file
with open('website_text.txt', 'r', encoding='utf-8') as f:
    base_prompt = f.read()

# Define the assistant's full prompt template
estella_assistant_template = base_prompt + """
You are the friendly virtual foodora rider assistant, named "Estela". 
Your expertise is in providing instructions and support to riders. 
This includes any general work related queries for foodora riders.
Answers need to be simple and short. In addition to that prioritise "important" tag when answering from the text.txt that are related to the question.
Include emojis in your responses to reflect the situation more naturally. 
You do not provide information outside of this scope. 
If a question is not about rider support, respond with, "This is a quirey I am unable to help you with. Please try to re-form your question or  please reach out to your nearest supervisor or create a ticket to HR-support." in the language the user is writing to you.
Question: {question} 
Answer:
"""

# Create the prompt template
prompt_template = PromptTemplate(
    input_variables=["question"],
    template=estella_assistant_template
)

# Instantiate the model
llm = ChatOpenAI(model='gpt-4o-mini', temperature=0, api_key=openai_api_key)

# Define the full chain
def query_llm(question):
    formatted_prompt = prompt_template.format(question=question)
    return llm.invoke(formatted_prompt).content

# Network utility functions
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def get_network_info():
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if "Default Gateway" in line:
                    return line.split(":")[-1].strip()
        else:
            result = subprocess.run(['ip', 'route', 'show', 'default'], capture_output=True, text=True)
            if result.returncode == 0:
                parts = result.stdout.split()
                if len(parts) >= 3:
                    return parts[2]
    except Exception as e:
        print(f"Could not get gateway: {e}")
    return None

# Flask App
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()
    question = data.get("question", "")
    response = query_llm(question)
    return jsonify({"response": response})

if __name__ == "__main__":
    local_ip = get_local_ip()
    gateway = get_network_info()
    port = 5000

    print(f"🚀 Starting Estela Assistant...")
    print(f"📱 Access from this device: http://localhost:{port}")
    print(f"🌐 Access from other devices: http://{local_ip}:{port}")
    if gateway:
        print(f"🏠 Gateway: {gateway}")
    app.run(host="0.0.0.0", port=port, debug=True)
