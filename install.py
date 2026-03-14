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
    
    # Interactive configuration
    domain = "localhost"
    email = "admin@your-domain.com"
    
    print("")
    use_domain = input("🌐 Do you want to configure a real domain for HTTPS? [y/N]: ").strip().lower()
    if use_domain == 'y':
        domain = input("   Enter your domain (e.g., ollama.example.com): ").strip()
        email = input("   Enter admin email (for Let's Encrypt notices): ").strip()
        if not domain: domain = "localhost"
        if not email: email = "admin@your-domain.com"
    
    origins = f"https://{domain}"
    
    with open(".env", "w") as f:
        f.write(f"OLLAMA_API_KEY={api_key}\n")
        f.write(f"WEBUI_SECRET_KEY={webui_secret}\n")
        f.write(f"DOMAIN={domain}\n")
        f.write(f"OLLAMA_ORIGINS={origins}\n")
        f.write(f"EMAIL_ADMIN={email}\n")
        f.write("CPU_LIMIT=4.00\n")
        f.write("MEMORY_LIMIT=16G\n")
    
    if domain != "localhost":
        print(f"✅ Configuration saved for {domain}. HTTPS will be activated automatically.")
    else:
        print("✅ .env file generated with default localhost settings.")
        
    # Optional Basic Auth
    if not os.path.exists("Caddyfile.ext"):
        with open("Caddyfile.ext", "w") as f:
            f.write("")
        print("")
        use_basic_auth = input("🔐 Do you want to protect the WebUI with a Basic Auth password? [y/N]: ").strip().lower()
        if use_basic_auth == 'y':
            import getpass
            auth_user = input("   Enter username for Basic Auth: ").strip()
            auth_pass = getpass.getpass("   Enter password for Basic Auth: ").strip()
            if auth_user and auth_pass:
                try:
                    hash_cmd = ["docker", "run", "--rm", "caddy:alpine", "caddy", "hash-password", "--plaintext", auth_pass]
                    auth_hash = subprocess.check_output(hash_cmd).decode('utf-8').strip()
                    with open("Caddyfile.ext", "w") as f:
                        f.write(f"basicauth {{\n    {auth_user} {auth_hash}\n}}\n")
                    print(f"✅ Basic Auth enabled for user '{auth_user}'.")
                except Exception as e:
                    print(f"❌ Failed to generate Basic Auth hash: {e}")
            else:
                print("   Skipping Basic Auth due to empty username or password.")
else:
    print("✅ Existing .env file detected.")

if not os.path.exists("Caddyfile.ext"):
    with open("Caddyfile.ext", "w") as f:
        f.write("")

# 3. Smart Hardware Detection (GPU vs CPU)
print("🔍 Analyzing available hardware...")

has_nvidia = has_nvidia_gpu()

cpus = "4.00"
memory = "16G"
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("CPU_LIMIT="):
                cpus = line.split("=", 1)[1].strip()
            elif line.startswith("MEMORY_LIMIT="):
                memory = line.split("=", 1)[1].strip()

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
