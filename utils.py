import os
import sys
import subprocess

def get_docker_compose_cmd():
    """Smart search for the docker-compose or docker compose plugin binary."""
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
        print("❌ Error: docker-compose or the docker compose plugin was not found.")
        sys.exit(1)

    return docker_compose_cmd

def has_nvidia_gpu():
    """Checks if an NVIDIA GPU is available and working."""
    try:
        return subprocess.run(["nvidia-smi"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
    except FileNotFoundError:
        return False

def generate_override_content(cpus, memory, has_gpu):
    """Generates the docker-compose.override.yml content correctly."""
    content = f"""services:
  ollama:
    deploy:
      resources:
        limits:
          cpus: '{cpus}'
          memory: {memory}
"""
    if has_gpu:
        content += """        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
"""
    return content
