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

# --- PATCH OpenTelemetry context detach to suppress ValueError on cross-context detach ---
try:
    import opentelemetry.context.contextvars_context
    _original_detach = opentelemetry.context.contextvars_context.ContextVarsRuntimeContext.detach
    def safe_detach(self, token):
        try:
            _original_detach(self, token)
        except ValueError as e:
            logging.getLogger("opentelemetry.context").warning(f"Suppressed context detach error: {e}")
    opentelemetry.context.contextvars_context.ContextVarsRuntimeContext.detach = safe_detach
except ImportError:
    pass
# --- END PATCH ---

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
logging.getLogger('agent.sub_agents.activity_agent').setLevel(logging.DEBUG)
logging.getLogger('langchain_community').setLevel(logging.DEBUG)

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to sys.path to allow imports
current_dir = str(pathlib.Path(__file__).parent.absolute())
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import key modules
from config import settings
from api.routes import create_router
from agent.root_agent import create_root_agent, initialize_agents

# Log the environment configuration
logger.info(f"Starting Travel Agent Backend - Mode: {'Vertex AI' if settings.USE_VERTEX_AI else 'Direct API'}, Model: {settings.MODEL}")

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

# Initialize agents
success = initialize_agents()
if success:
    logger.info("All agents initialized successfully")
else:
    logger.warning("Some agents failed to initialize")

# Setup the root agent
root_agent = create_root_agent()
if root_agent:
    logger.info(f"Root agent created: {root_agent.name if hasattr(root_agent, 'name') else 'Direct API mode'}")
else:
    logger.warning("Failed to create root agent")

# Create and include API routes
router = create_router(root_agent)
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    port = settings.PORT
    host = settings.HOST
    
    logger.info(f"Starting server on {host}:{port}")

    # When running directly, use the direct path
    uvicorn.run("main:app", host=host, port=port, reload=True)
