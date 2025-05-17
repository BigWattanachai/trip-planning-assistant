#!/bin/bash

# Run script for Trip Planning Assistant Backend (Improved)
# This script ensures the backend is run in the correct environment and mode

# Change to the script's directory
cd "$(dirname "$0")"

# Load environment variables if .env exists
if [ -f .env ]; then
    echo "Loading environment variables from .env"
    export $(grep -v '^#' .env | xargs)
fi

# Check if TAVILY_API_KEY is set
if [ -z "$TAVILY_API_KEY" ]; then
    echo "WARNING: TAVILY_API_KEY environment variable is not set."
    echo "Tavily search will not be available."
else
    echo "Tavily API key is set. Tavily search will be available."
fi

# Check if ADK mode is enabled
if [ "$GOOGLE_GENAI_USE_VERTEXAI" = "1" ] || [ "$GOOGLE_GENAI_USE_VERTEXAI" = "true" ]; then
    echo "Running in Vertex AI (ADK) mode"
    
    # Check for ADK requirements
    python3 -c "import google.adk" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "WARNING: google-adk package is not installed."
        echo "Install it with: pip install google-adk"
        echo "Falling back to Direct API mode"
        export GOOGLE_GENAI_USE_VERTEXAI=0
    fi
else
    echo "Running in Direct API mode"
    
    # Check for GOOGLE_API_KEY in Direct API mode
    if [ -z "$GOOGLE_API_KEY" ]; then
        echo "ERROR: GOOGLE_API_KEY environment variable is not set."
        echo "This is required for Direct API mode."
        echo "Set it in your .env file or environment."
        exit 1
    fi
fi

# Set PYTHONPATH to include the current directory
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# Run the application
echo "Starting Trip Planning Assistant Backend..."
python3 main.py
