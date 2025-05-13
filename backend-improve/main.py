"""
Main entry point for the Travel A2A Backend (Improved).
This module starts the FastAPI server and handles API requests.
"""

import os
import uvicorn
import logging
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("travel_a2a.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import the required modules from backend_improve
try:
    import backend_improve
    from backend_improve.api import router
    logger.info("Successfully imported modules from backend_improve")
except ImportError:
    # Fall back to direct imports if not running as a package
    logger.info("Using direct imports")
    from api import router

# Create the FastAPI app
app = FastAPI(
    title="Travel A2A Backend",
    description="Backend API for Travel A2A application with enhanced Tavily search",
    version="2.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the API router with /api prefix
app.include_router(router, prefix="/api")

# Get application mode
USE_VERTEX_AI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes")
MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")
PORT = int(os.getenv("PORT", "8000"))

@app.get("/")
async def root():
    """Root endpoint that provides basic information about the API"""
    return {
        "name": "Travel A2A Backend API",
        "version": "2.0",
        "description": "Backend API for Travel A2A application with enhanced search capabilities",
        "mode": "Vertex AI (ADK)" if USE_VERTEX_AI else "Direct API",
        "model": MODEL,
        "documentation": "/docs",
    }

def main():
    """Main entry point for the application"""
    logger.info(f"Starting Travel A2A Backend in {'Vertex AI (ADK)' if USE_VERTEX_AI else 'Direct API'} mode")
    logger.info(f"Using model: {MODEL}")
    logger.info(f"Tavily search available: {os.getenv('TAVILY_API_KEY') is not None}")

    # Initialize backend components

    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )

if __name__ == "__main__":
    main()
