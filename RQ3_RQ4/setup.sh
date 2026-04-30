#!/bin/bash
# RCI-SG Experiment Environment Setup Script
# Compatible with Ubuntu 22.04 / macOS 13+

set -e

echo "======================================"
echo "RCI-SG Experiment Setup"
echo "======================================"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Create virtual environment
echo "[1/5] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "[2/5] Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "[3/5] Installing Python dependencies..."
pip install -r requirements.txt

# Check OpenClaw installation
echo "[4/5] Checking OpenClaw..."
if command -v openclaw &> /dev/null; then
    echo "OpenClaw version: $(openclaw --version)"
else
    echo "[WARNING] OpenClaw not found. Install with: npm install -g openclaw@latest"
fi

# Check Node.js
echo "[5/5] Checking Node.js..."
if command -v node &> /dev/null; then
    echo "Node.js version: $(node --version)"
else
    echo "[WARNING] Node.js not found. Install from https://nodejs.org/"
fi

# Verify OpenAI SDK
echo ""
echo "Verifying OpenAI SDK..."
python3 -c "from openai import OpenAI; print('OpenAI SDK OK')"

echo ""
echo "======================================"
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Configure Bailian API key in ~/.openclaw/openclaw.json"
echo "  2. Edit config/experiment.yaml for your setup"
echo "  3. Run: source venv/bin/activate && python -m src.experiment_runner"
echo "======================================"
