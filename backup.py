#!/usr/bin/env python3
# backup.py - Secure backup of Open-WebUI chats and user data

import os
import sys
import subprocess
import time
from utils import get_docker_compose_cmd

# Ensure we are in the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("💾 Starting Open-WebUI backup...")

# 1. Get docker compose command
docker_compose_cmd = get_docker_compose_cmd()

# 2. Define backup file name with timestamp
timestamp = time.strftime("%Y%m%d_%H%M%S")
backup_filename = f"openwebui_backup_{timestamp}.tar.gz"

print("⏸️ Pausing the WebUI container to ensure data consistency...")
subprocess.run(docker_compose_cmd + ["pause", "webui"])

try:
    print(f"📦 Compressing chat database and user settings into {backup_filename}...")
    
    # Use a temporary busybox container mounted to the data volume to tar it
    # This avoids needing to know the exact path on the host OS
    subprocess.run([
        "docker", "run", "--rm",
        "-v", "ollama-hardened_open-webui_data:/data:ro",
        "-v", f"{os.getcwd()}:/backup",
        "alpine", "tar", "-czf", f"/backup/{backup_filename}", "-C", "/data", "."
    ], check=True)
    
    print(f"✅ Backup successfully created: {backup_filename}")
    
except subprocess.CalledProcessError as e:
    print(f"❌ Error during backup: {e}")
finally:
    print("▶️ Unpausing the WebUI container...")
    subprocess.run(docker_compose_cmd + ["unpause", "webui"])

print("========================================================")
print("🎉 Backup complete! Keep this file safe.")
print("========================================================")
