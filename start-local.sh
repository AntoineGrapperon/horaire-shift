#!/bin/bash

# Exit on error
set -e

echo "Starting ShiftMed Local Development Environment (Streamlit-only)..."

# Check if .venv exists, if not create it
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "Installing/Updating dependencies..."
pip install -r requirements.txt

# Start the Streamlit app
echo "Starting Streamlit App on http://localhost:8501"
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
