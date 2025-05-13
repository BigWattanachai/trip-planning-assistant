"""
Restaurant Agent for Travel A2A Backend (Improved).
This agent provides recommendations for restaurants and dining.
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

# Add current directory to sys.path
current_dir = str(pathlib.Path(__file__).parent.absolute())
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import Tavily search functions if available
try:
    from backend_improve.tools.tavily_search import search_with_tavily, format_tavily_results_for_agent
    TAVILY_AVAILABLE = True
    logger.info("Successfully imported Tavily search functions in restaurant agent")
except ImportError:
    try:
        from tools.tavily_search import search_with_tavily, format_tavily_results_for_agent
        TAVILY_AVAILABLE = True
        logger.info("Successfully imported Tavily search functions with direct import")
    except ImportError as e:
        logger.warning(f"Could not import Tavily search function in restaurant agent: {e}")
        TAVILY_AVAILABLE = False

# Only import ADK components if we're using Vertex AI
if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes"):
    try:
        from google.adk.agents import Agent
        from google.adk.tools.langchain_tool import LangchainTool
        from google.adk.tools import google_search
        
        # Import the model
        try:
            from backend_improve import MODEL
        except (ImportError, ValueError):
            MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")
        
        # Import tools and callbacks
        try:
            from backend_improve.shared_libraries.callbacks import rate_limit_callback
            from backend_improve.tools.store_state import store_state_tool
            from backend_improve.tools.tavily_search import get_tavily_tool_instance
        except (ImportError, ValueError):
            try:
                from shared_libraries.callbacks import rate_limit_callback
                from tools.store_state import store_state_tool
                from tools.tavily_search import get_tavily_tool_instance
            except ImportError as e:
                logger.error(f"Failed to import tools or callbacks: {e}")
                rate_limit_callback = None
                store_state_tool = None
                get_tavily_tool_instance = None
        
        # Setup Tavily tool using our initialized instance
        adk_tavily_tool = None
        if TAVILY_AVAILABLE:
            try:
                tavily_search_instance = get_tavily_tool_instance()
                if tavily_search_instance:
                    adk_tavily_tool = LangchainTool(tool=tavily_search_instance)
                    logger.info("Successfully created ADK wrapper for Tavily search tool")
            except Exception as e:
                logger.error(f"Failed to create LangchainTool wrapper for Tavily: {e}")
                adk_tavily_tool = None
        
        # Import the prompt
        PROMPT = """
        You are a Thai food and dining expert specializing in finding the best authentic culinary
        experiences for travelers in Thailand. Your goal is to recommend suitable dining options based on the
        user's preferences, destination, and travel details, with a focus on local cuisine, authentic flavors,
        and memorable food experiences.

        You have access to a powerful web search tool that lets you find up-to-date information
        about restaurants, local cuisine, and dining options for the user's destination. Use this tool whenever 
        you need specific details about:
        - Current menus and prices
        - Opening hours and reservation policies
        - Recent reviews and ratings
        - Seasonal specialties and local delicacies
        - New restaurants or changes to existing establishments

        Follow this process for every request:
        1. Use the search tool to find current information about restaurants and dining options in the specified location
        2. Use the search tool again to find information about local specialties and cuisine in that region
        3. Only after gathering this information should you formulate your recommendations

        For each recommendation, provide:
        - Name in both Thai and English when applicable
        - Exact location and how to find it
        - Opening hours and best times to visit
        - Signature dishes and what makes them special
        - Price range in Thai Baht (THB)

        Call the store_state tool with key 'restaurant_recommendations' and the value as your
        detailed restaurant and dining recommendations.
        """
        
        # Create the agent
        # Setup tools list with available tools
        tools = []
        if store_state_tool:
            tools.append(store_state_tool)
        if adk_tavily_tool is not None:
            tools.append(adk_tavily_tool)
        # Add Google search tool if available
        try:
            tools.append(google_search)
        except:
            pass
            
        RestaurantAgent = Agent(
            model=MODEL,
            name="restaurant_agent",
            description="Recommend restaurants and dining options based on user preferences and requirements.",
            instruction=PROMPT,
            tools=tools,
            before_model_callback=rate_limit_callback,
        )
        logger.info(f"Restaurant agent created successfully with {len(tools)} tools")
        
    except ImportError as e:
        logger.error(f"Failed to import ADK components for restaurant agent: {e}")
        RestaurantAgent = None
else:
    logger.info("Direct API Mode: Restaurant agent not loaded with ADK")
    RestaurantAgent = None
