#!/bin/bash
# install_dependencies.sh
# Installs system and python dependencies from local sources for air-gapped environment.

set -e

# Configuration
REPO_DIR="./offline_repo"
PIP_DIR="./offline_pip"

echo "Starting offline dependency installation..."

# 1. System Packages (apt)
if [ -d "$REPO_DIR" ]; then
    echo "Installing system packages from $REPO_DIR..."
    # Assuming user has placed .deb files in REPO_DIR
    # Option A: dpkg -i
    sudo dpkg -i "$REPO_DIR"/*.deb || echo "Warning: Some dependencies might be missing. Ensure all .debs are present."
    
    # Option B: Local apt repository (more robust but requires setup)
    # echo "deb [trusted=yes] file:$(pwd)/$REPO_DIR ./" | sudo tee /etc/apt/sources.list.d/local.list
    # sudo apt-get update
    # sudo apt-get install -y python3-pip python3-venv ffmpeg
else
    echo "Error: $REPO_DIR directory not found. Please transfer .deb files."
    exit 1
fi

# 2. Python Environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 3. Python Packages (pip)
if [ -d "$PIP_DIR" ]; then
    echo "Installing Python packages from $PIP_DIR..."
    # Install using local wheels/tarballs
    pip install --no-index --find-links="$PIP_DIR" -r requirements.txt
else
    echo "Error: $PIP_DIR directory not found. Please transfer pip packages."
    exit 1
fi

echo "Dependency installation complete."
