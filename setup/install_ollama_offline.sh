#!/bin/bash
# install_ollama_offline.sh
# Installs Ollama binary and sets up systemd service in air-gapped environment.

set -e

INSTALL_DIR="/usr/local/bin"
OLLAMA_BINARY="./ollama-linux-amd64" # Assumed filename of the transferred binary

echo "Starting offline Ollama installation..."

# 1. Verify Binary
if [ ! -f "$OLLAMA_BINARY" ]; then
    echo "Error: Ollama binary ($OLLAMA_BINARY) not found."
    echo "Please download 'ollama-linux-amd64' from the official site and place it here."
    exit 1
fi

# 2. Install Binary
echo "Installing binary to $INSTALL_DIR..."
sudo cp "$OLLAMA_BINARY" "$INSTALL_DIR/ollama"
sudo chmod +x "$INSTALL_DIR/ollama"

# 3. Create User
echo "Creating ollama user..."
sudo useradd -r -s /bin/false -U -m -d /usr/share/ollama ollama || echo "User ollama already exists."

# 4. Setup Systemd Service
echo "Configuring systemd service..."
SERVICE_FILE="/etc/systemd/system/ollama.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=$INSTALL_DIR/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_MODELS=/usr/share/ollama/.ollama/models"

[Install]
WantedBy=default.target
EOF

# 5. Enable and Start
echo "Enabling and starting Ollama service..."
sudo systemctl daemon-reload
sudo systemctl enable ollama
sudo systemctl start ollama

echo "Ollama installation complete. Check status with: systemctl status ollama"
