#!/bin/bash
# run.sh — activates venv and runs the library app

PROJECT_DIR=$(pwd)

# Check we're in the right directory
if [ ! -f "main.py" ]; then
    echo "✗ main.py not found. Run this from the project root."
    exit 1
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "⚠ No venv found — running with system Python"
fi

echo "Starting Library Management System..."
echo "════════════════════════════════════"
python3 main.py