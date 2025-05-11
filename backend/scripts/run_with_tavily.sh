#!/bin/bash

# Script to run the travel agent backend with Tavily integration

# Check if TAVILY_API_KEY is set
if [ -z "$TAVILY_API_KEY" ]; then
    echo "TAVILY_API_KEY environment variable is not set!"
    echo "Please set it with: export TAVILY_API_KEY=your_api_key_here"
    echo "or add it to your .env file"
    exit 1
fi

echo "========================================="
echo "Starting Travel A2A Backend with Tavily"
echo "========================================="
echo "TAVILY_API_KEY is set with length: ${#TAVILY_API_KEY}"
echo ""

# Test Tavily integration
echo "Testing Tavily integration..."
python scripts/test_tavily.py
if [ $? -ne 0 ]; then
    echo "Tavily test failed! Check your API key and dependencies."
    exit 1
fi

echo ""
echo "Tavily integration tested successfully!"
echo ""
echo "Starting the application..."
echo "========================================="

# Run the application
python main.py
