import os
import json
from flask import Flask, render_template, request, jsonify
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Session storage file
SESSION_FILE = 'user_sessions.json'

def load_sessions():
    try:
        with open(SESSION_FILE, 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_sessions():
    with open(SESSION_FILE, 'w') as f:
        json.dump(list(user_sessions), f)

# Load existing sessions on startup
user_sessions = load_sessions()

# Read prompt base from file
prompt = open('website_text.txt', 'r', encoding='utf-8').read()

# Define assistant template
estella_assistant_template = prompt + """
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

# LangChain Prompt Template
estella_assistant_prompt_template = PromptTemplate(
    input_variables=["question"],
    template=estella_assistant_template
)

# LLM configuration
llm = ChatOpenAI(
    model='gpt-4o-mini',
    temperature=0,
    api_key=""
)

llm_chain = estella_assistant_prompt_template | llm

def query_llm(question):
    response = llm_chain.invoke({'question': question})
    return response.content

# Twilio credentials
TWILIO_ACCOUNT_SID = "AC94d95f3c136457ba5f95f2fcda0c803e"
TWILIO_AUTH_TOKEN = "dbb8eec575876cef63b4da98cecd5c87"
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/")
def index():
    welcome_message = (
        "👋 Hi, I'm *Estella*.\n\n"
        "This is a virtual conversation, which means I am just a tool to guide you. "
        "Please note that this is not a human interaction. "
        "You still need to report your accident/incident through the form attached or create a ticket to HR."
    )
    return render_template("index.html", welcome_message=welcome_message)

@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()
    question = data["question"]
    response = query_llm(question)
    return jsonify({"response": response})

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_message = request.values.get("Body", "").strip()
    sender_phone = request.values.get("From", "")
    
    response = MessagingResponse()
    
    if sender_phone not in user_sessions:
        user_sessions.add(sender_phone)
        save_sessions()

        intro_message = (
            "👋 Hi, I'm *Estella*.\n\n"
            "This is a virtual conversation, which means I am just a tool to guide you. "
            "Please note that this is not a human interaction. "
            "You still need to report your accident/incident through the form attached or create a ticket to HR."
        )
        
        response.message(intro_message)

        if incoming_message:
            bot_response = query_llm(incoming_message)
            response.message(bot_response)
    else:
        bot_response = query_llm(incoming_message)
        response.message(bot_response)
    
    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
