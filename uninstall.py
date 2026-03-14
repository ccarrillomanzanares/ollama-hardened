#!/usr/bin/env python3
# uninstall.py - Secure and granular uninstallation

import os
import sys
import subprocess
from utils import get_docker_compose_cmd

# Ensure we are in the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Smart binary search
docker_compose_cmd = get_docker_compose_cmd()

print("🧹 Starting Ollama Hardened uninstallation process...\n")

# 1. Ask about containers
stop_containers = input("❓ Do you want to stop and remove the containers (Ollama and Proxy)? [y/N]: ").strip().lower()
if stop_containers in ['y', 'yes']:
    print("🛑 Stopping and removing containers...")
    subprocess.run(docker_compose_cmd + ["down"])
else:
    print("⏭️  Skipping: Containers will keep running.")

# 2. Ask about data
print("")
delete_volumes = input("❓ Do you want to remove the data volumes as well? (This will permanently delete the downloaded models) [y/N]: ").strip().lower()
if delete_volumes in ['y', 'yes']:
    print("🗑️ Removing Docker volumes...")
    subprocess.run(docker_compose_cmd + ["down", "-v"])
else:
    print("📦 Keeping data volumes (models and certificates).")

# 3. Clean configuration files
print("")
delete_config = input("❓ Do you want to delete local configuration files (.env, API Key, GPU config)? [y/N]: ").strip().lower()
if delete_config in ['y', 'yes']:
    print("🗑️ Deleting .env and docker-compose.override.yml...")
    if os.path.exists(".env"): os.remove(".env")
    if os.path.exists("docker-compose.override.yml"): os.remove("docker-compose.override.yml")
else:
    print("📄 Keeping configuration files.")

print("")
print("========================================================")
print("✅ Uninstallation process finished.")
print("========================================================")
