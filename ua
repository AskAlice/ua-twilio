#! /bin/bash
#!/bin/bash

# Path to the virtual environment's activate script
VENV_PATH="venv/bin/activate"

# Check if the virtual environment activation script exists
if [ ! -f "$VENV_PATH" ]; then
    echo "Virtual environment activation script not found. To create run 'python3 -m venv venv, then run 'source venv/bin/activate' to activate the virtual environment and install the required packages with 'pip install -r requirements.txt"
    exit 1
fi

# Activate the virtual environment

source venv/bin/activate
if [ ! -f .env ]
then
  export $(cat .env | xargs)
fi
# Execute the Python script with all passed arguments
python ./ua.py "$@"

# Deactivate the virtual environment (optional)
deactivate