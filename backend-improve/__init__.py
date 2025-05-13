"""
Travel A2A Backend - Improved Version
This package contains the backend code for the Travel A2A application.
It supports both Vertex AI (Google ADK) and Direct API modes.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Determine mode: Vertex AI (ADK) or Direct API
USE_VERTEX_AI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes")

# Get model name from environment variables with fallback
MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")

# Initialize Tavily search
from .tools.tavily_search import initialize_tavily_search
TAVILY_AVAILABLE = initialize_tavily_search() is not None

print(f"Backend initialized in {'Vertex AI (ADK)' if USE_VERTEX_AI else 'Direct API'} mode")
print(f"Using model: {MODEL}")
print(f"Tavily search available: {TAVILY_AVAILABLE}")
