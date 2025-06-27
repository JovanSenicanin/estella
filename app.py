from flask import Flask, render_template, request, jsonify
from langchain_openai import ChatOpenAI 
from langchain.prompts import PromptTemplate
import os
import socket
import subprocess
import platform
import socket

os.environ["OPENAI_API_KEY"] = "sk-proj-b199YOxjL0CxWM11ozg2T3BlbkFJidoS82AtjQkjzIVmBwY7"

# Read the prompt from the file
prompt = open('website_text.txt', 'r', encoding='utf-8').read()

# Define the assistant's template
estella_assistant_template = prompt + """
You are the friendly virtual foodora rider assistant, named "Estela". 
Your expertise is in providing instructions and support to riders. 
This includes any general work related queries for foodora riders.
Answers need to be simple and short. In addition to that prioritise "important" tag when answering from the text.txt that are related to the question.
Include emojis in your responses to reflect the situation more naturally. 
You do not provide information outside of this scope. 
If a question is not about rider support, respond with, "This is out of my scope to answer, sorry!"
Question: {question} 
Answer: 
"""

# Create the prompt template
estella_assistant_prompt_template = PromptTemplate(
    input_variables=["question"],
    template=estella_assistant_template
)

# Use ChatOpenAI for chat models
llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

# Chain the prompt template with the LLM
llm_chain = estella_assistant_prompt_template | llm

def query_llm(question):
    response = llm_chain.invoke({'question': question})
    return response.content  # Access the content attribute directly

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def get_network_info():
    """Get network information including gateway"""
    import subprocess
    import platform
    
    try:
        if platform.system() == "Windows":
            # Windows command to get network info
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            current_adapter = None
            gateway = None
            
            for line in lines:
                if "Wireless LAN adapter" in line or "Ethernet adapter" in line:
                    current_adapter = line.strip()
                elif "Default Gateway" in line and current_adapter:
                    gateway = line.split(':')[-1].strip()
                    if gateway and gateway != "":
                        break
            
            return gateway
        else:
            # Linux/Mac command to get gateway
            result = subprocess.run(['ip', 'route', 'show', 'default'], capture_output=True, text=True)
            if result.returncode == 0:
                # Extract gateway IP from output like "default via 192.168.1.1 dev wlan0"
                parts = result.stdout.split()
                if len(parts) >= 3:
                    return parts[2]
            
            # Fallback for Mac
            result = subprocess.run(['route', '-n', 'get', 'default'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'gateway:' in line:
                    return line.split(':')[1].strip()
                    
    except Exception as e:
        print(f"Could not get gateway: {e}")
    
    return None

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.get_json()
    question = data["question"]
    response = query_llm(question)
    return jsonify({"response": response})

if __name__ == "__main__":
    local_ip = get_local_ip()
    gateway = get_network_info()
    port = 5000
    
    print(f"🚀 Starting Estela Assistant...")
    print(f"📱 Access from this device: http://localhost:{port}")
    print(f"🌐 Access from other devices using your IP: http://{local_ip}:{port}")
    
    if gateway:
        print(f"🏠 Network Gateway (Router IP): {gateway}")
        print(f"💡 If devices can't connect, try these solutions:")
        print(f"   1. Use your actual IP: http://{local_ip}:{port}")
        print(f"   2. Check if devices are on same subnet (first 3 numbers should match)")
        print(f"   3. Disable Windows Firewall temporarily to test")
        print(f"   4. Try gateway IP range (e.g., if gateway is {gateway})")
    
    print(f"📶 Make sure all devices are connected to the same WiFi network!")
    print(f"🔧 If connection fails, check firewall settings!")
    
    # host='0.0.0.0' makes the app accessible on all network interfaces
    app.run(host='0.0.0.0', port=port, debug=True)