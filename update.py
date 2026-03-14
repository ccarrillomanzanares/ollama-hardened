#!/usr/bin/env python3
# update.py - Secure and automated update for Ollama Hardened

import os
import sys
import subprocess
from utils import get_docker_compose_cmd

# Ensure we are in the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Smart binary search for docker compose
docker_compose_cmd = get_docker_compose_cmd()

print("🔄 Starting Ollama Hardened update process...\n")

# 1. Pull the latest images
print("⬇️  Pulling the latest images for Ollama and Caddy...")
pull_process = subprocess.run(docker_compose_cmd + ["pull"])
if pull_process.returncode != 0:
    print("❌ Error pulling images. Please check your internet connection and Docker status.")
    sys.exit(1)

# 2. Recreate containers with the new images
print("\n♻️  Recreating containers with the updated images...")
# Note: We run 'down' first to prevent 'ContainerConfig' KeyError in older docker-compose v1.29.x
down_process = subprocess.run(docker_compose_cmd + ["down"])
if down_process.returncode != 0:
    print("⚠️ Warning: Could not cleanly stop existing containers, continuing anyway...")

up_process = subprocess.run(docker_compose_cmd + ["up", "-d"])
if up_process.returncode != 0:
    print("❌ Error recreating containers. The service might be down.")
    sys.exit(1)

# 3. Optional Cleanup
print("\n🧹 Do you want to remove the old, unused Docker images to free up disk space?")
cleanup = input("   (This is safe and won't affect your downloaded AI models) [Y/n]: ").strip().lower()
if cleanup in ['', 'y', 'yes']:
    print("🗑️  Cleaning up old images...")
    subprocess.run(["docker", "image", "prune", "-f"])
    print("✅ Cleanup finished.")
else:
    print("⏭️  Skipping image cleanup.")

print("\n========================================================")
print("🎉 Ollama Hardened successfully updated!")
print("========================================================")