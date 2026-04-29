#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")"

VENV_DIR="venv"

# Check for virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv "$VENV_DIR"
    
    # Activate and install requirements
    source "$VENV_DIR/bin/activate"
    if [ -f "requirements.txt" ]; then
        echo "Installing requirements..."
        pip install --upgrade pip
        pip install -r requirements.txt
    else
        echo "Error: requirements.txt not found. Cannot install dependencies."
        exit 1
    fi
else
    # Activate existing environment
    source "$VENV_DIR/bin/activate"
fi

# Launch the application
echo "Starting ThreadStepper..."
python3 start.py
