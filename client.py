#!/usr/bin/env python3
# client.py - Interactive Python client for Ollama Hardened

import os
import sys
import json
import urllib.request
import urllib.error
import ssl

# Ensure we are in the script's directory to read .env
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 1. Load configuration from .env
env_vars = {}
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                env_vars[key] = val
else:
    print("❌ Error: .env file not found. Make sure to run ./install.py first.")
    sys.exit(1)

API_KEY = env_vars.get("OLLAMA_API_KEY")
if not API_KEY:
    print("❌ Error: OLLAMA_API_KEY is not defined in the .env file.")
    sys.exit(1)

DOMAIN = env_vars.get("DOMAIN", "localhost")
BASE_URL = f"https://{DOMAIN}"

# Disable SSL verification if localhost
ssl_context = ssl.create_default_context()
if DOMAIN == "localhost":
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

def make_request(endpoint, method="GET", payload=None, stream=False):
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    data = json.dumps(payload).encode('utf-8') if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        response = urllib.request.urlopen(req, context=ssl_context)
        if stream:
            return response
        return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print("")
        print(f"❌ HTTP Error {e.code}: {e.read().decode('utf-8', errors='ignore')}")
        return None
    except urllib.error.URLError as e:
        print("")
        print(f"❌ Connection Error: {e.reason}")
        return None

def pause():
    print("")
    input("Press Enter to continue...")

def list_models():
    print("")
    print("--- Installed Models ---")
    data = make_request("/api/tags")
    if data and "models" in data:
        models = data["models"]
        if not models:
            print("No models installed.")
        else:
            for m in models:
                size = m.get("details", {}).get("parameter_size", "unknown")
                print(f"- {m['name']} ({size})")
    return data.get("models", []) if data else []

def download_model():
    print("")
    print("--- Download Model ---")
    print("Select a popular model to download:")
    print("1) llama3       (Meta - 8B)")
    print("2) mistral      (Mistral AI - 7B)")
    print("3) qwen2:0.5b   (Alibaba - Fast/Light)")
    print("4) phi3         (Microsoft - 3.8B)")
    print("5) gemma2       (Google - 9B)")
    print("6) ✍️ Custom    (Enter model name manually)")
    print("0) ❌ Cancel")
    
    choice = input("Choose an option [0-6]: ").strip()
    model = ""
    if choice == '1': model = "llama3"
    elif choice == '2': model = "mistral"
    elif choice == '3': model = "qwen2:0.5b"
    elif choice == '4': model = "phi3"
    elif choice == '5': model = "gemma2"
    elif choice == '6': model = input("Enter custom model name (e.g., deepseek-coder): ").strip()
    elif choice == '0': return
    else:
        print("Invalid option.")
        return

    if model:
        print(f"Downloading '{model}'... (This may take several minutes)")
        response_stream = make_request("/api/pull", method="POST", payload={"name": model}, stream=True)
        
        if response_stream:
            try:
                for line in response_stream:
                    if line:
                        chunk = json.loads(line.decode('utf-8'))
                        status = chunk.get("status", "")
                        # Clear line and print status
                        sys.stdout.write(f"\r\033[KProcessing: {status}")
                        sys.stdout.flush()
                print("")
                print("")
                print("Download finished!")
            except Exception as e:
                print("")
                print(f"Error reading stream: {e}")

def chat():
    print("")
    print("--- Chat Mode ---")
    data = make_request("/api/tags")
    models = [m['name'] for m in data.get("models", [])] if data else []
    
    if not models:
        print("No models installed. Please download a model first (Option 2).")
        return

    print("Select an installed model to chat with:")
    for i, name in enumerate(models, 1):
        print(f"{i}) {name}")
    print("0) ❌ Cancel")
    
    choice = input(f"Choose an option [0-{len(models)}]: ").strip()
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(models):
        if choice != '0': print("Invalid option.")
        return
        
    selected_model = models[int(choice)-1]
    print("")
    print(f"Starting chat with {selected_model}... (Type 'exit' to quit)")
    print("-" * 51)
    
    while True:
        prompt = input("You: ").strip()
        if prompt.lower() in ['exit', 'quit', '']:
            break
            
        payload = {
            "model": selected_model,
            "prompt": prompt,
            "stream": True # We use true for Python to get typing effect!
        }
        
        sys.stdout.write("AI: ")
        sys.stdout.flush()
        
        response_stream = make_request("/api/generate", method="POST", payload=payload, stream=True)
        if response_stream:
            for line in response_stream:
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    sys.stdout.write(chunk.get("response", ""))
                    sys.stdout.flush()
                    if chunk.get("done"):
                        break
        print() # New line after answer

def health_check():
    print("")
    print("--- Server Health Status ---")
    try:
        url = f"{BASE_URL}/health"
        req = urllib.request.Request(url)
        res = urllib.request.urlopen(req, context=ssl_context)
        print(f"Status Code: {res.getcode()} - {res.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error checking health: {e}")

def main():
    while True:
        # Clear screen for Windows/Linux
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=================================================")
        print("🤖 Ollama Hardened Python Client")
        print(f"🔗 Server: {BASE_URL}")
        print("=================================================")
        print("1. 📋 List installed models")
        print("2. ⬇️  Download a new model (Pull)")
        print("3. 💬 Chat with a model")
        print("4. 🏥 Check server health status")
        print("5. ❌ Exit")
        print("=================================================")
        
        option = input("Select an option [1-5]: ").strip()
        
        if option == '1':
            list_models()
            pause()
        elif option == '2':
            download_model()
            pause()
        elif option == '3':
            chat()
            pause()
        elif option == '4':
            health_check()
            pause()
        elif option == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid option.")
            import time; time.sleep(1)

if __name__ == "__main__":
    main()
