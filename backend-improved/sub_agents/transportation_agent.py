"""
Transportation recommendations for the Travel Agent.
Integrates Tavily search for real-time information about transportation options.
"""

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

from config import settings
from agent.tools.tavily_search import tavily_search, tavily_search_with_tool_context

# Only import ADK components if we're using Vertex AI
vertex_ai_mode = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes")
logger.info(f"Vertex AI mode: {vertex_ai_mode}")

# Try to initialize Tavily for potential future use
tavily_available = bool(settings.TAVILY_API_KEY)
logger.info(f"Tavily search availability: {tavily_available}")

if vertex_ai_mode:
    try:
        from google.adk.agents import Agent
        from google.adk.tools import Tool
        from google.adk.tools.langchain_tool import LangchainTool
        
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
            from ..agent.tools.store_state import store_state_tool
        except (ImportError, ValueError):
            # Fall back to absolute imports
            from shared_libraries.callbacks import rate_limit_callback
            from agent.tools.store_state import store_state_tool
        
        # Import the prompt
        try:
            # Try relative import first
            from . import transportation_agent_prompt
        except (ImportError, ValueError):
            # Fall back to absolute import
            from sub_agents import transportation_agent_prompt
        
        # Create the Tavily search tool for ADK
        adk_tavily_tool = None
        if tavily_available:
            try:
                # Create a Tool wrapper for the tavily_search_with_tool_context function
                adk_tavily_tool = Tool(
                    function=tavily_search_with_tool_context,
                    description="Search for real-time information about transportation options using Tavily search API",
                    name="tavily_search"
                )
                logger.info("Successfully created ADK wrapper for Tavily search tool")
            except Exception as e:
                logger.error(f"Failed to create Tool wrapper for Tavily: {e}")
                adk_tavily_tool = None
            
        # Setup tools list with available tools
        tools = [store_state_tool]
        if adk_tavily_tool is not None:
            tools.append(adk_tavily_tool)
            
        # Create the agent
        TransportationAgent = Agent(
            model=MODEL,
            name="transportation_agent",
            description=(
                "Recommend transportation options based on user preferences and requirements."
            ),
            instruction=transportation_agent_prompt.PROMPT,
            tools=tools,
            before_model_callback=rate_limit_callback,
        )
        logger.info(f"Transportation agent created successfully with {len(tools)} tools")
        
    except ImportError as e:
        logger.error(f"Failed to import ADK components for transportation agent: {e}")
        TransportationAgent = None
else:
    logger.info("Direct API Mode: Transportation agent not loaded with ADK")
    
    # For Direct API mode, we can still initialize Tavily and make it available
    if tavily_available:
        try:
            # Create a simple transportation search function for Direct API mode
            def search_transportation_with_tavily(query, origin=None, destination=None):
                """
                Search for transportation information using Tavily search.
                
                Args:
                    query (str): The search query
                    origin (str, optional): Origin location to focus the search on
                    destination (str, optional): Destination location to focus the search on
                
                Returns:
                    dict: Search results or None if search failed
                """
                try:
                    # Add location context if provided
                    search_query = query
                    if origin and destination:
                        search_query = f"{query} from {origin} to {destination}"
                    elif destination:
                        search_query = f"{query} to {destination}"
                        
                    logger.info(f"Direct API Mode: Searching Tavily for transportation: {search_query}")
                    
                    result = tavily_search(search_query)
                    
                    # Log success and result summary
                    result_len = len(str(result)) if result else 0
                    logger.info(f"Direct API Mode: Tavily transportation search successful. Result length: {result_len} chars")
                    
                    return result
                except Exception as e:
                    logger.error(f"Direct API Mode: Tavily transportation search error: {e}")
                    return None
                
            # Make the search function globally available
            TransportationAgent = None
            transportation_tavily_search = search_transportation_with_tavily
            logger.info("Direct API Mode: Tavily transportation search function created and ready for use")
        except Exception as e:
            logger.error(f"Direct API Mode: Failed to create Tavily transportation search function: {e}")
            TransportationAgent = None
            transportation_tavily_search = None
    else:
        logger.info("Direct API Mode: Tavily search not available for transportation agent")
        TransportationAgent = None
        transportation_tavily_search = None
