#!/usr/bin/env bash
set -e

echo "[*] Setting up Clipboard Server..."

# Detect OS
OS=$(uname -s)
echo "[*] Detected OS: $OS"

# Go to script directory
cd "$(dirname "$0")"

# Ensure Python & Pip
echo "[*] Installing Python & Pip..."
if [[ "$OS" == "Linux" ]]; then
    sudo apt-get update -y
    sudo apt-get install -y python3 python3-pip curl unzip

elif [[ "$OS" == "Darwin" ]]; then
    # Check if Homebrew exists
    if ! command -v brew &>/dev/null; then
        echo "[*] Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        eval "$(/opt/homebrew/bin/brew shellenv)"  # Ensure brew is in PATH for Apple Silicon
    fi
    brew install python3 curl unzip

elif [[ "$OS" == MINGW* || "$OS" == CYGWIN* || "$OS" == MSYS* ]]; then
    # Check if Chocolatey exists
    if ! command -v choco &>/dev/null; then
        echo "[*] Installing Chocolatey..."
        powershell.exe -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command \
            "Set-ExecutionPolicy Bypass -Scope Process; \
            [System.Net.ServicePointManager]::SecurityProtocol = 'Tls12'; \
            iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
        export PATH="$PATH:/c/ProgramData/chocolatey/bin"
    fi
    choco install python curl unzip -y

else
    echo "[!] Unsupported OS. Install Python 3.10+ manually."
    exit 1
fi

# Install Python packages
echo "[*] Installing Python dependencies..."
pip3 install --user flask flask_sqlalchemy pyngrok pyyaml

# Add ~/.local/bin to PATH
export PATH="$HOME/.local/bin:$PATH"

# Read authtoken from config.yaml
AUTHTOKEN=$(python3 -c "import yaml;print(yaml.safe_load(open('config.yaml'))['server'].get('ngrok_authtoken',''))")
if [ -n "$AUTHTOKEN" ]; then
    echo "[*] Adding ngrok authtoken..."
    ngrok config add-authtoken "$AUTHTOKEN"
else
    echo "[!] No ngrok_authtoken found in config.yaml"
fi

# Start server
echo "[*] Starting Clipboard Server with ngrok..."
python3 server.py
