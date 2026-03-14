#!/usr/bin/env python3
# install.py - Secure deployment of Ollama Hardened

import os
import sys
import subprocess
import secrets
import string

# Ensure we are in the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("🔒 Starting Ollama Hardened deployment...")

# 1. Smart Docker Compose search
docker_compose_cmd = None

try:
    if subprocess.run(["docker", "compose", "version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        docker_compose_cmd = ["docker", "compose"]
except FileNotFoundError:
    pass

if not docker_compose_cmd:
    try:
        if subprocess.run(["docker-compose", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            docker_compose_cmd = ["docker-compose"]
    except FileNotFoundError:
        pass

if not docker_compose_cmd:
    if os.path.isfile("/home/ccmai/.docker-compose/docker-compose"):
        docker_compose_cmd = ["/home/ccmai/.docker-compose/docker-compose"]

if not docker_compose_cmd:
    print("❌ Error: docker-compose or the docker compose plugin was not found.")
    sys.exit(1)

print(f"✅ Using: {' '.join(docker_compose_cmd)}")

# 2. Secure API Key generation if it does not exist
if not os.path.exists(".env"):
    print("🔑 Generating a new secure API Key and .env configuration...")
    # Generate 32 alphanumeric characters
    alphabet = string.ascii_letters + string.digits
    api_key = ''.join(secrets.choice(alphabet) for _ in range(32))
    
    with open(".env", "w") as f:
        f.write(f"OLLAMA_API_KEY={api_key}\n")
        f.write("DOMAIN=localhost\n")
        f.write("OLLAMA_ORIGINS=https://localhost\n")
        f.write("EMAIL_ADMIN=admin@your-domain.com\n")
    print("✅ .env file generated. You can change DOMAIN, OLLAMA_ORIGINS and EMAIL to activate automatic HTTPS.")
else:
    print("✅ Existing .env file detected.")

# 3. Smart Hardware Detection (GPU vs CPU)
print("🔍 Analyzing available hardware...")

override_content = """services:
  ollama:
    deploy:
      resources:
        limits:
          cpus: '4.00'
          memory: 16G
"""

has_nvidia = False
try:
    if subprocess.run(["nvidia-smi"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        has_nvidia = True
except FileNotFoundError:
    pass

if has_nvidia:
    print("⚡ NVIDIA GPU detected! Activating hardware acceleration.")
    override_content += """        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
"""
else:
    print("🐢 No NVIDIA GPU detected. Using CPU mode (Limits: 4 Cores, 16GB RAM).")

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
