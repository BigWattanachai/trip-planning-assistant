"""Transportation recommendations for the Travel Agent."""

import os
import sys
import pathlib
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to allow imports
parent_dir = str(pathlib.Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Only import ADK components if we're using Vertex AI
if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes"):
    try:
        from google.adk.agents import Agent
        
        # Import the model
        try:
            # First try relative import
            from .. import MODEL
        except (ImportError, ValueError):
            # Fall back to absolute import
            MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")
        
        # Import tools and callbacks
        try:
            # Try relative imports first
            from ..shared_libraries.callbacks import rate_limit_callback
            from ..tools.store_state import store_state_tool
        except (ImportError, ValueError):
            # Fall back to absolute imports
            from backend.shared_libraries.callbacks import rate_limit_callback
            from backend.tools.store_state import store_state_tool
        
        # Import the prompt
        try:
            # Try relative import first
            from . import transportation_agent_prompt
        except (ImportError, ValueError):
            # Fall back to absolute import
            from backend.sub_agents import transportation_agent_prompt
        
        # Create the agent
        TransportationAgent = Agent(
            model=MODEL,
            name="transportation_agent",
            description=(
                "Recommend transportation options based on user travel details."
            ),
            instruction=transportation_agent_prompt.PROMPT,
            tools=[store_state_tool],
            before_model_callback=rate_limit_callback,
        )
        logger.info("Transportation agent created successfully")
        
    except ImportError as e:
        logger.error(f"Failed to import ADK components for transportation agent: {e}")
        TransportationAgent = None
else:
    logger.info("Direct API Mode: Transportation agent not loaded")
    TransportationAgent = None
