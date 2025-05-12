"""Activity recommendations for the Travel Agent."""

import os
import sys
import pathlib
import logging
import warnings

# Configure logging
logger = logging.getLogger(__name__)

from backend.tools.tavily_search import initialize_tavily_search, get_tavily_tool_instance

# Add the parent directory to sys.path to allow imports
parent_dir = str(pathlib.Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Only import ADK components if we're using Vertex AI
vertex_ai_mode = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes")
logger.info(f"Vertex AI mode: {vertex_ai_mode}")
print(f"Vertex AI mode: {vertex_ai_mode}")

# Try to initialize Tavily regardless of mode for potential future use
print("About to initialize Tavily search tool...")
tavily_search_instance = initialize_tavily_search()
print(f"Tavily search initialization result: {tavily_search_instance is not None}")

if vertex_ai_mode:
    try:
        from google.adk.agents import Agent
        from google.adk.tools.langchain_tool import LangchainTool
        
        # Setup Tavily tool using our initialized instance
        adk_tavily_tool = None
        if tavily_search_instance:
            try:
                adk_tavily_tool = LangchainTool(tool=tavily_search_instance)
                logger.info("Successfully created ADK wrapper for Tavily search tool")
            except Exception as e:
                logger.error(f"Failed to create LangchainTool wrapper for Tavily: {e}")
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
    logger.info("Direct API Mode: Activity agent not loaded with ADK")
    print("Direct API Mode: Activity agent not loaded with ADK")
    
    # For Direct API mode, we can still initialize Tavily and make it available
    if tavily_search_instance:
        try:
            # Create a simple activity agent handler for Direct API mode
            # This function could be called directly from the main agent
            def search_with_tavily(query, location=None):
                """
                Search for travel information using Tavily search.
                
                Args:
                    query (str): The search query
                    location (str, optional): Location to focus the search on
                
                Returns:
                    dict: Search results or None if search failed
                """
                if tavily_search_instance:
                    try:
                        # Add location context if provided
                        search_query = query
                        if location:
                            search_query = f"{query} in {location}"
                            
                        logger.info(f"Direct API Mode: Searching Tavily for: {search_query}")
                        print(f"Direct API Mode: Searching Tavily for: {search_query}")
                        
                        result = tavily_search_instance.invoke(search_query)
                        
                        # Log success and result summary
                        result_len = len(str(result)) if result else 0
                        logger.info(f"Direct API Mode: Tavily search successful. Result length: {result_len} chars")
                        print(f"Direct API Mode: Tavily search successful. Result length: {result_len} chars")
                        
                        return result
                    except Exception as e:
                        logger.error(f"Direct API Mode: Tavily search error: {e}")
                        print(f"Direct API Mode: Tavily search error: {e}")
                        return None
                else:
                    logger.warning("Direct API Mode: Tavily search not available")
                    print("Direct API Mode: Tavily search not available")
                    return None
                
            # Make the search function globally available
            ActivityAgent = None
            activity_tavily_search = search_with_tavily
            logger.info("Direct API Mode: Tavily search function created and ready for use")
            print("Direct API Mode: Tavily search function created and ready for use")
        except Exception as e:
            logger.error(f"Direct API Mode: Failed to create Tavily search function: {e}")
            print(f"Direct API Mode: Failed to create Tavily search function: {e}")
            ActivityAgent = None
            activity_tavily_search = None
    else:
        logger.info("Direct API Mode: Tavily search not available")
        print("Direct API Mode: Tavily search not available")
        ActivityAgent = None
        activity_tavily_search = None
