#!/bin/bash
# Quick start script for Linux Mint Debian Edition

echo "Starting Interlinear Text Creator..."
echo ""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Install with: sudo apt install python3"
    exit 1
fi

# Check for tkinter
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: Tkinter is not installed."
    echo "Install with: sudo apt install python3-tk"
    exit 1
fi

# Check for required packages
python3 -c "import qrcode" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required Python packages..."
    pip3 install -r requirements.txt
fi

# Run the application
python3 -m interlinear.app
