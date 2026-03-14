# 🛡️ Ollama Hardened Deployment (Enterprise-Grade)

A production-ready, Zero-Trust, and "Air-Gapped" architecture to run [Ollama](https://ollama.com/) securely. It includes automatic HTTPS via Let's Encrypt, strong authentication via API Key, an integrated chat UI (Open WebUI), and strict container configuration. Ideal for exposing AI to corporate development teams or in public clouds.

> **The Problem:** Ollama is designed to be plug-and-play locally, so it lacks authentication, exposes port 11434 in plain text, and does not support native TLS.
> **The Solution:** This stack encapsulates Ollama and Open WebUI in an isolated network, protected by a "Gatekeeper" (Caddy) that automatically manages SSL certificates and blocks any unauthorized requests.

## 🌟 Defense-in-Depth Architecture

1. **Gatekeeper (Caddy Proxy)**: An ultra-lightweight reverse proxy acting as the sole entry point.
2. **Automatic HTTPS (Let's Encrypt)**: Interactive setup configures a real domain to automatically manage and renew TLS certificates. If you use `localhost`, it generates a self-signed one.
3. **Strong Authentication (API Key)**: Immediate blocking (401 Unauthorized) at the proxy for API access if the request does not include the valid `X-API-Key` header.
4. **Isolated Backend Network**: The Ollama and WebUI containers reside in a dedicated Docker network. They have no ports exposed to the physical host and can only be accessed through the Gatekeeper.
5. **Immutable File System**: Core containers run in `read_only: true` mode to prevent malware injection. Legitimate writes are limited to temporary in-memory volumes (`tmpfs`).
6. **Least Privilege (Cap Drop)**: All kernel administrator privileges are dropped (`cap_drop: ALL`). Containers cannot escalate privileges (`no-new-privileges`).
7. **Smart Hardware Detection & Dynamic Resources**: The installer automatically detects if there is an NVIDIA GPU. If it exists, it activates it; if not, it configures CPU and RAM limits to protect the host based on `.env` configuration. You can easily reconfigure these limits using the interactive Python client.
8. **Automatic Healthchecks & Resiliency**: Docker monitors the health of Caddy, Ollama, and Open WebUI in real-time, automatically restarting them if they fail or become unresponsive.
9. **Log Rotation**: Strict log rotation policies (10MB per file, max 3 files) prevent Docker logs from filling up your server's disk over time.
10. **Optional Basic Auth**: Add an extra layer of security with network-level Basic Authentication to hide the WebUI login page from public scanners.

## 🚀 Quick Installation and Usage

### Requirements
* Docker and Docker Compose (V2) installed.
* (Optional) A domain or subdomain pointing to your server's IP (for real HTTPS).

### Step 1: Install and configure

\`\`\`bash
git clone https://github.com/YourUser/ollama-hardened.git
cd ollama-hardened
./install.py
\`\`\`

The script is interactive. It will:
- Automatically generate a secure, randomly generated alphanumeric `OLLAMA_API_KEY` and `WEBUI_SECRET_KEY` in a `.env` file.
- Ask if you want to configure a real domain for HTTPS. If yes, it sets up CORS and Let's Encrypt seamlessly.
- Ask if you want to protect the Open WebUI with a Basic Auth password.
- Detect your hardware and set appropriate resource limits.

### Step 2: Manage services

The project includes a robust `Makefile` (Recommended for SysAdmins):

* \`make start\`: Starts the containers in the background.
* \`make stop\`: Stops the containers.
* \`make restart\`: Restarts the services.
* \`make logs\`: Shows logs in real-time.
* \`make status\`: Shows the status of the containers.
* \`make health\`: Shows the real-time healthcheck status of the services.
* \`make backup\`: Securely pauses the WebUI, creates a `.tar.gz` backup of all your chats and users, and unpauses it.
* \`make clean\`: **DANGER** Stops everything, deletes data volumes, and removes your configuration files.

### 🐍 Interactive Python Client

The project includes an interactive client to interact with your secure Ollama instance from the terminal:

\`\`\`bash
./client.py
\`\`\`

From the client menu you can:
- List installed models.
- Download new models (with real-time progress).
- Chat directly with models.
- **Dynamically configure CPU/RAM resource limits** without editing files manually.
- Check the server health status.

### 🧹 Secure Uninstallation

To uninstall the infrastructure securely without using `make clean` (which drops everything), use the interactive uninstaller:

\`\`\`bash
./uninstall.py
\`\`\`
*(The script will ask if you want to keep the data volumes—like your downloaded models—and will ask if you want to delete your `.env` file for security).*

## 📡 How to connect via API

To use the API programmatically, you must **always** send the `X-API-Key` header. Traffic goes over HTTPS.

**Example with cURL:**
\`\`\`bash
# Replace 'localhost' with your domain if configured
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

---
*If you find this architecture useful for your infrastructure, consider leaving a ⭐ on GitHub and contributing improvements.*
