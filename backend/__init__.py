"""Initialization functions for Travel Agent."""

import logging
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
loglevel = os.getenv("TRAVEL_AGENT_LOG_LEVEL", "INFO")
numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError(f"Invalid log level: {loglevel}")
logger = logging.getLogger(__package__)
logger.setLevel(numeric_level)

# Determine if using Vertex AI or direct Gemini API
USE_VERTEX_AI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes")

if USE_VERTEX_AI:
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        # Initialize Vertex AI if project and location are provided
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        
        if project_id:
            logger.info(f"Initializing Vertex AI with project: {project_id}, location: {location}")
            vertexai.init(project=project_id, location=location)
        else:
            logger.warning("GOOGLE_CLOUD_PROJECT not set. Vertex AI initialization skipped.")
            
    except ImportError:
        logger.warning("vertexai package not found. Falling back to direct Gemini API.")
        USE_VERTEX_AI = False

# Set up Gemini API if not using Vertex AI or if Vertex AI initialization failed
if not USE_VERTEX_AI:
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        logger.info("Initializing Gemini API directly")
        genai.configure(api_key=api_key)
    else:
        logger.warning("GOOGLE_API_KEY not set. Gemini API initialization failed.")

# Set the model to use
MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-1.5-flash")
logger.info(f"Using model: {MODEL}")

# Define a simplified Agent class that can work with both Gemini API and ADK
class SimpleAgent:
    def __init__(self, name, description, instruction):
        self.name = name
        self.description = description
        self.instruction = instruction
        self.model = genai.GenerativeModel(MODEL)
    
    async def generate_content(self, prompt):
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return f"Error: {str(e)}"
