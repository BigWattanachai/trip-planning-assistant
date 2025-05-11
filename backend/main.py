"""
Travel Agent Backend: Main application entry point
"""
import os
import sys
import pathlib
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("travel_a2a.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set specific loggers to DEBUG level
logging.getLogger('sub_agents.activity_agent').setLevel(logging.DEBUG)
logging.getLogger('langchain_community').setLevel(logging.DEBUG)

# Log the Tavily API key status
tavily_api_key = os.getenv("TAVILY_API_KEY")
if tavily_api_key:
    logger.info(f"TAVILY_API_KEY is set with length {len(tavily_api_key)}")
else:
    logger.warning("TAVILY_API_KEY environment variable is not set.")

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to sys.path to allow imports
parent_dir = str(pathlib.Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Add the current directory to sys.path
current_dir = str(pathlib.Path(__file__).parent.absolute())
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Use direct imports when running within the backend directory
try:
    # First try relative import in case we're running as a package
    from api.routes import router 
except ImportError:
    # If that fails, try an absolute import
    from backend.api.routes import router

# Log the environment configuration
USE_VERTEX_AI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes")
MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")
logger.info(f"Starting Travel Agent Backend - Mode: {'Vertex AI' if USE_VERTEX_AI else 'Direct API'}, Model: {MODEL}")

# Create FastAPI application
app = FastAPI(title="Travel Agent Backend")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")

    # When running directly, use the direct path
    uvicorn.run("main:app", host=host, port=port, reload=True)
