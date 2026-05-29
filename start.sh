#!/bin/bash

echo "========================================"
echo "AI PR Review Assistant"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python version: $PYTHON_VERSION"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo
    echo "Please edit .env file with your API keys:"
    echo "- CLAUDE_API_KEY (required)"
    echo "- GITHUB_TOKEN (optional, for private repos)"
    echo
    read -p "Press Enter to continue..."
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt
echo

# Run installation test
echo "Running installation test..."
python3 test_install.py
echo

# Start the application
echo "Starting AI PR Review Assistant..."
echo "Open http://localhost:5000 in your browser"
echo
echo "Press Ctrl+C to stop the server"
echo
python3 app.py
