# 🛡️ Ollama Hardened Deployment (Enterprise-Grade)

A production-ready, Zero-Trust, and "Air-Gapped" architecture to run [Ollama](https://ollama.com/) securely. It includes automatic HTTPS via Let's Encrypt, strong authentication via API Key, and strict container configuration. Ideal for exposing AI to corporate development teams or in public clouds.

> **The Problem:** Ollama is designed to be plug-and-play locally, so it lacks authentication, exposes port 11434 in plain text, and does not support native TLS.
> **The Solution:** This stack encapsulates Ollama in an isolated network, protected by a "Gatekeeper" (Caddy) that automatically manages SSL certificates and blocks any unauthorized requests.

## 🌟 Defense-in-Depth Architecture

1. **Gatekeeper (Caddy Proxy)**: An ultra-lightweight reverse proxy acting as the sole entry point.
2. **Automatic HTTPS (Let's Encrypt)**: If you configure a valid domain, the proxy automatically manages and renews TLS certificates. If you use `localhost`, it generates a self-signed one.
3. **Strong Authentication (API Key)**: Immediate blocking (401 Unauthorized) at the proxy if the request does not include the valid `X-API-Key` header. Malicious traffic never reaches Ollama.
4. **Isolated Backend Network**: The Ollama container resides in a dedicated Docker network. It has no ports exposed to the physical host and can only be accessed through the Gatekeeper.
5. **Immutable File System**: Both containers run in `read_only: true` mode to prevent malware injection. Legitimate writes are limited to temporary in-memory volumes (`tmpfs`).
6. **Least Privilege (Cap Drop)**: All kernel administrator privileges are dropped (`cap_drop: ALL`). Containers cannot escalate privileges (`no-new-privileges`).
7. **Smart Hardware Detection**: The installer automatically detects if there is an NVIDIA GPU. If it exists, it activates it; if not, it configures CPU and RAM limits to protect the host.
8. **Automatic Healthchecks**: Docker monitors the health of Ollama and Caddy in real-time, automatically restarting them if they fail.

## 🚀 Quick Installation and Usage

### Requirements
* Docker and Docker Compose (V2) installed.
* (Optional) A domain or subdomain pointing to your server's IP (for real HTTPS).

### Step 1: Install and generate key

\`\`\`bash
git clone https://github.com/YourUser/ollama-hardened.git
cd ollama-hardened
./install.py
\`\`\`

The script will automatically generate a `.env` file with a secure, randomly generated alphanumeric `OLLAMA_API_KEY`.

### Step 2: Configure Automatic HTTPS (Optional but recommended)

Open the generated `.env` file and edit the variables:

\`\`\`env
OLLAMA_API_KEY=YourSuperSecureGeneratedKey123
DOMAIN=ollama.mycompany.com      # Put your real domain here
EMAIL_ADMIN=admin@mycompany.com   # Email for Let's Encrypt notices
\`\`\`

### Step 3: Start the service

You can use the installation script again, or if you prefer, use the included `Makefile` (Recommended for SysAdmins):

* \`make start\`: Starts the containers in the background.
* \`make stop\`: Stops the containers.
* \`make logs\`: Shows logs in real-time (useful to see if Let's Encrypt validated your domain).
* \`make reload\`: Applies changes to the `.env` or configuration.
* \`make clean\`: **DANGER** Stops everything, deletes data volumes, and removes your API Key.

### 🧹 Secure Uninstallation

To uninstall the infrastructure, the project includes an interactive script that protects you from accidentally deleting the downloaded AI models (which usually weigh several Gigabytes):

\`\`\`bash
./uninstall.py
\`\`\`
*(The script will ask if you want to keep the data volumes and will ask if you want to delete your `.env` file for security to avoid leaving orphaned keys).*

## 📡 How to connect (Client)

To use the API, you must **always** send the `X-API-Key` header. Traffic must now go over `https://`.

**Example with cURL:**
\`\`\`bash
# Replace 'localhost' with your domain if you configured it
curl -H "X-API-Key: YourSuperSecureGeneratedKey123" https://localhost/api/tags
\`\`\`

**Example in Python (using the \`requests\` library):**
\`\`\`python
import requests

headers = {"X-API-Key": "YourSuperSecureGeneratedKey123"}
# Use your real domain in the URL
response = requests.get("https://ollama.mycompany.com/api/tags", headers=headers)
print(response.json())
\`\`\`

## 🛠️ Customization and GPU

By default, the configuration is ready to delegate all available NVIDIA GPUs (`deploy.resources.reservations.devices.driver: nvidia`).
If you do not have a GPU on your server, the container will use the CPU automatically (limited to 4 cores by `docker-compose.override.yml` generated during installation to protect the host). You can adjust these limits according to your hardware.

---
*If you find this architecture useful for your infrastructure, consider leaving a ⭐ on GitHub and contributing improvements.*
