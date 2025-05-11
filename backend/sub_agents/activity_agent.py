"""Activity recommendations for the Travel Agent."""

import os
import sys
import pathlib
import logging
import warnings

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
        from google.adk.tools.langchain_tool import LangchainTool
        
        # Check for Tavily API Key
        if not os.getenv("TAVILY_API_KEY"):
            warnings.warn("TAVILY_API_KEY environment variable not set. Tavily search tool will not function properly.")
        
        # Import Tavily search tool
        try:
            from langchain_community.tools import TavilySearchResults
            # Initialize Tavily search tool
            tavily_search = TavilySearchResults(
                max_results=5,
                search_depth="advanced",
                include_answer=True,
                include_raw_content=True,
                include_images=True,
            )
            # Wrap with LangchainTool
            adk_tavily_tool = LangchainTool(tool=tavily_search)
            logger.info("Tavily search tool initialized successfully")
        except ImportError as e:
            logger.error(f"Failed to import Tavily search tool: {e}")
            adk_tavily_tool = None
            
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
            from . import activity_agent_prompt
        except (ImportError, ValueError):
            # Fall back to absolute import
            from backend.sub_agents import activity_agent_prompt
        
        # Create the agent
        # Setup tools list with available tools
        tools = [store_state_tool]
        if adk_tavily_tool is not None:
            tools.append(adk_tavily_tool)
            
        ActivityAgent = Agent(
            model=MODEL,
            name="activity_agent",
            description=(
                "Recommend activities and attractions based on user preferences and requirements."
            ),
            instruction=activity_agent_prompt.PROMPT,
            tools=tools,
            before_model_callback=rate_limit_callback,
        )
        logger.info(f"Activity agent created successfully with {len(tools)} tools")
        
    except ImportError as e:
        logger.error(f"Failed to import ADK components for activity agent: {e}")
        ActivityAgent = None
else:
    logger.info("Direct API Mode: Activity agent not loaded")
    ActivityAgent = None
