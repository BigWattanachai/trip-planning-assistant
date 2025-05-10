"""Activity recommendations for the Travel Agent."""

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
            MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-1.5-flash-002")
        
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
            from . import activity_agent_prompt
        except (ImportError, ValueError):
            # Fall back to absolute import
            from backend.sub_agents import activity_agent_prompt
        
        # Create the agent
        ActivityAgent = Agent(
            model=MODEL,
            name="activity_agent",
            description=(
                "Recommend activities and attractions based on user preferences and requirements."
            ),
            instruction=activity_agent_prompt.PROMPT,
            tools=[store_state_tool],
            before_model_callback=rate_limit_callback,
        )
        logger.info("Activity agent created successfully")
        
    except ImportError as e:
        logger.error(f"Failed to import ADK components for activity agent: {e}")
        ActivityAgent = None
else:
    logger.info("Direct API Mode: Activity agent not loaded")
    ActivityAgent = None
