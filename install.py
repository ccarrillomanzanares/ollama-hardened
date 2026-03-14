#!/usr/bin/env python3
# install.py - Secure deployment of Ollama Hardened

import os
import sys
import subprocess
import secrets
import string
from utils import get_docker_compose_cmd, has_nvidia_gpu, generate_override_content

# Ensure we are in the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("🔒 Starting Ollama Hardened deployment...")

# 1. Smart Docker Compose search
docker_compose_cmd = get_docker_compose_cmd()

print(f"✅ Using: {' '.join(docker_compose_cmd)}")

# 2. Secure API Key generation if it does not exist
if not os.path.exists(".env"):
    print("🔑 Generating a new secure API Key and .env configuration...")
    # Generate keys
    alphabet = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(alphabet) for _ in range(32))
    webui_secret = ''.join(secrets.choice(alphabet) for _ in range(64))
    
    with open(".env", "w") as f:
        f.write(f"OLLAMA_API_KEY={api_key}\n")
        f.write(f"WEBUI_SECRET_KEY={webui_secret}\n")
        f.write("DOMAIN=localhost\n")
        f.write("OLLAMA_ORIGINS=https://localhost\n")
        f.write("EMAIL_ADMIN=admin@your-domain.com\n")
    print("✅ .env file generated. You can change DOMAIN, OLLAMA_ORIGINS and EMAIL to activate automatic HTTPS.")
else:
    print("✅ Existing .env file detected.")

# 3. Smart Hardware Detection (GPU vs CPU)
print("🔍 Analyzing available hardware...")

has_nvidia = has_nvidia_gpu()
cpus = "4.00"
memory = "16G"

if has_nvidia:
    print("⚡ NVIDIA GPU detected! Activating hardware acceleration.")
else:
    print(f"🐢 No NVIDIA GPU detected. Using CPU mode (Limits: {cpus} Cores, {memory} RAM).")

override_content = generate_override_content(cpus, memory, has_nvidia)

with open("docker-compose.override.yml", "w") as f:
    f.write(override_content)

# 4. Deployment
print("🚀 Starting containers securely...")
subprocess.run(docker_compose_cmd + ["up", "-d"])

# Read API key to display it
api_key_to_show = ""
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("OLLAMA_API_KEY="):
                api_key_to_show = line.split("=", 1)[1].strip()
                break

print("")
print("========================================================")
print("🎉 Ollama Hardened successfully deployed!")
print("========================================================")
if api_key_to_show:
    print(f"Your API Key is: {api_key_to_show}")
print("========================================================")
