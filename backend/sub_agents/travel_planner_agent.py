"""Travel Planner coordination for the Travel Agent."""

import os
import sys
import pathlib
import logging

# Configure logging
logger = logging.getLogger(__name__)

from backend.tools.tavily_search import initialize_tavily_search, get_tavily_tool_instance

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
            from . import travel_planner_agent_prompt
        except (ImportError, ValueError):
            # Fall back to absolute import
            from backend.sub_agents import travel_planner_agent_prompt
        
        # Create the agent
        TravelPlannerAgent = Agent(
            model=MODEL,
            name="travel_planner_agent",
            description=(
                "Create a comprehensive travel plan by integrating recommendations from specialized agents."
            ),
            instruction=travel_planner_agent_prompt.PROMPT,
            tools=[store_state_tool],
            before_model_callback=rate_limit_callback,
        )
        logger.info("Travel planner agent created successfully")
        
    except ImportError as e:
        logger.error(f"Failed to import ADK components for travel planner agent: {e}")
        TravelPlannerAgent = None
else:
    logger.info("Direct API Mode: Travel planner agent not loaded")
    TravelPlannerAgent = None
