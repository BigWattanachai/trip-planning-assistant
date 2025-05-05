from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
from dotenv import load_dotenv

from routes.api import router as api_router
from utils.middleware import setup_middleware

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Travel A2A API",
    description="AI-powered travel planning API using Google ADK and MCP",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Set up middleware
setup_middleware(app)

# Include API routes
app.include_router(api_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Travel A2A API",
        "version": "1.0.0",
        "description": "AI-powered travel planning using Google ADK and MCP",
        "documentation": "/api/docs"
    }

@app.on_event("startup")
async def startup_event():
    """Execute on server startup"""
    logger.info("Starting Travel A2A API server")
    logger.info(f"API documentation available at: http://localhost:{os.getenv('PORT', '8000')}/api/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Execute on server shutdown"""
    logger.info("Shutting down Travel A2A API server")

if __name__ == "__main__":
    # Get server configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    env = os.getenv("ENV", "development")
    
    # Run server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=(env == "development"),
        log_level="info"
    )
