"""
Travel planner agent for the Travel Agent.
Integrates Tavily search for comprehensive travel planning with real-time information.
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
            from . import travel_planner_agent_prompt
        except (ImportError, ValueError):
            # Fall back to absolute import
            from sub_agents import travel_planner_agent_prompt
        
        # Create the Tavily search tool for ADK
        adk_tavily_tool = None
        if tavily_available:
            try:
                # Create a Tool wrapper for the tavily_search_with_tool_context function
                adk_tavily_tool = Tool(
                    function=tavily_search_with_tool_context,
                    description="Search for real-time travel information using Tavily search API",
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
        TravelPlannerAgent = Agent(
            model=MODEL,
            name="travel_planner_agent",
            description=(
                "Create comprehensive travel plans based on user preferences and requirements."
            ),
            instruction=travel_planner_agent_prompt.PROMPT,
            tools=tools,
            before_model_callback=rate_limit_callback,
        )
        logger.info(f"Travel planner agent created successfully with {len(tools)} tools")
        
    except ImportError as e:
        logger.error(f"Failed to import ADK components for travel planner agent: {e}")
        TravelPlannerAgent = None
else:
    logger.info("Direct API Mode: Travel planner agent not loaded with ADK")
    
    # For Direct API mode, we can still initialize Tavily and make it available
    if tavily_available:
        try:
            # Create a simple travel planner search function for Direct API mode
            def plan_travel_with_tavily(query, origin=None, destination=None, dates=None):
                """
                Search for comprehensive travel planning information using Tavily search.
                
                Args:
                    query (str): The search query
                    origin (str, optional): Origin location
                    destination (str, optional): Destination location
                    dates (str, optional): Travel dates
                
                Returns:
                    dict: Search results or None if search failed
                """
                try:
                    # Add context if provided
                    search_query = query
                    context_parts = []
                    
                    if origin and destination:
                        context_parts.append(f"from {origin} to {destination}")
                    elif destination:
                        context_parts.append(f"to {destination}")
                        
                    if dates:
                        context_parts.append(f"during {dates}")
                        
                    if context_parts:
                        context = " ".join(context_parts)
                        search_query = f"{query} {context}"
                        
                    logger.info(f"Direct API Mode: Searching Tavily for travel planning: {search_query}")
                    
                    result = tavily_search(search_query)
                    
                    # Log success and result summary
                    result_len = len(str(result)) if result else 0
                    logger.info(f"Direct API Mode: Tavily travel planning search successful. Result length: {result_len} chars")
                    
                    return result
                except Exception as e:
                    logger.error(f"Direct API Mode: Tavily travel planning search error: {e}")
                    return None
                
            # Make the search function globally available
            TravelPlannerAgent = None
            travel_planner_tavily_search = plan_travel_with_tavily
            logger.info("Direct API Mode: Tavily travel planning search function created and ready for use")
        except Exception as e:
            logger.error(f"Direct API Mode: Failed to create Tavily travel planning search function: {e}")
            TravelPlannerAgent = None
            travel_planner_tavily_search = None
    else:
        logger.info("Direct API Mode: Tavily search not available for travel planner agent")
        TravelPlannerAgent = None
        travel_planner_tavily_search = None
