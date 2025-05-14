""" 
Travel A2A Backend - Improved Version
This package contains the backend code for the Travel A2A application.
It supports both Vertex AI (Google ADK) and Direct API modes.
"""

import os
import logging
import logging.handlers
from dotenv import load_dotenv

# Configure root logger
def setup_logging():
    """Set up application-wide logging configuration."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Check if a file handler is already set up
    has_file_handler = False
    for handler in root_logger.handlers:
        if isinstance(handler, logging.FileHandler):
            has_file_handler = True
            break
    
    if not has_file_handler:
        log_file_path = 'travel_a2a.log'
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Add console handler if needed
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # Log that we've initialized logging
        logging.info("Logging initialized for Travel A2A Backend")

# Set up logging immediately
setup_logging()

# Load environment variables
load_dotenv()

# Determine mode: Vertex AI (ADK) or Direct API
USE_VERTEX_AI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes")

# Get model name from environment variables with fallback
MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")

# Initialize Tavily search
from .tools.tavily_search import initialize_tavily_search
TAVILY_AVAILABLE = initialize_tavily_search() is not None

logging.info(f"Backend initialized in {'Vertex AI (ADK)' if USE_VERTEX_AI else 'Direct API'} mode")
logging.info(f"Using model: {MODEL}")
logging.info(f"Tavily search available: {TAVILY_AVAILABLE}")
