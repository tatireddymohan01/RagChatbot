#!/bin/bash
# Azure App Service startup script for FastAPI

# Install dependencies if needed
if [ -f requirements.txt ]; then
    pip install --no-cache-dir -r requirements.txt
fi

# Start the application with Uvicorn
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
