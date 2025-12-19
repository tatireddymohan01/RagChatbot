#!/bin/bash
# Azure App Service startup script for FastAPI

echo "Starting RAG Chatbot deployment..."

# Ensure we're in the correct directory
cd /home/site/wwwroot

# List files for debugging
echo "Files in wwwroot:"
ls -la

# Check Python version
python --version

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set PYTHONPATH
export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH

# Start the application with Uvicorn
echo "Starting Uvicorn server..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info
