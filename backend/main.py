"""
Travel A2A Backend: Main application entry point
"""
import os
import sys
import pathlib
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Handle imports for both running as a module and running directly
try:
    # When running as a module (python -m backend.main)
    from .api.routes import router
except ImportError:
    # When running directly (python main.py)
    # Add the parent directory to sys.path
    parent_dir = str(pathlib.Path(__file__).parent.parent.absolute())
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)

    # Use absolute imports
    from backend.api.routes import router

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(title="Travel A2A Backend")

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
    import sys
    import pathlib

    # Add the parent directory to sys.path to allow running directly
    parent_dir = str(pathlib.Path(__file__).parent.parent.absolute())
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    # When running directly, use the module path
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
