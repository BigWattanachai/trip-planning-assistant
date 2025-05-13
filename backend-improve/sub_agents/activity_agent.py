"""
Activity Agent for Travel A2A Backend (Improved).
This agent provides recommendations for activities and attractions.
It is enhanced with Tavily search for up-to-date information.
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

# Import Tavily search functions
try:
    from backend_improve.tools.tavily_search import search_with_tavily, format_tavily_results_for_agent
    TAVILY_AVAILABLE = True
    logger.info("Successfully imported Tavily search functions in activity agent")
except ImportError:
    try:
        from tools.tavily_search import search_with_tavily, format_tavily_results_for_agent
        TAVILY_AVAILABLE = True
        logger.info("Successfully imported Tavily search functions with direct import")
    except ImportError as e:
        logger.warning(f"Could not import Tavily search function in activity agent: {e}")
        TAVILY_AVAILABLE = False

# Only import ADK components if we're using Vertex AI
if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes"):
    try:
        from google.adk.agents import Agent
        from google.adk.tools.langchain_tool import LangchainTool
        
        # Import the model
        try:
            # First try backend-prefix import
            from backend_improve import MODEL
        except (ImportError, ValueError):
            # Fall back to environment variable
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
        You are an activities and attractions expert specializing in finding the best things to do
        for travelers in Thailand. Your goal is to recommend suitable activities and attractions based on the
        user's preferences, destination, and travel details, with a focus on nature-based experiences,
        local cultural immersion, and authentic Thai experiences.

        You have access to a powerful web search tool called Tavily that lets you find up-to-date information
        about attractions, activities, events, and local experiences in Thailand. Use this tool whenever you need
        specific details about:
        - Current operating hours, entrance fees, or conditions of attractions
        - Seasonal activities or events happening during the user's travel dates
        - Newly opened attractions or experiences not in your knowledge base
        - Detailed information about specific locations or activities the user is interested in
        - Current travel conditions, weather considerations, or local advisories

        When using the Tavily search tool:
        1. Formulate specific search queries rather than general ones
        2. Include the destination name in your query for more relevant results
        3. Use search to verify information before providing it to users
        4. Search for current or seasonal events that might be happening during the user's visit
        5. Always check for recent reviews and updates on popular attractions

        For each recommendation, provide:
        - Name in both Thai and English when applicable
        - Brief description highlighting what makes it special
        - Exact location and how to get there
        - Opening hours and best time to visit
        - Price range in Thai Baht (THB)
        - Insider tips that enhance the experience

        Format your response in a clear, structured way with headings for different categories of activities.
        If the user has specified a multi-day trip, organize recommendations by day with a logical flow
        based on proximity and pacing. Include a mix of active and relaxing experiences.

        Call the store_state tool with key 'activity_recommendations' and the value as your
        detailed activity recommendations.
        """
        
        # Create the agent
        # Setup tools list with available tools
        tools = []
        if store_state_tool:
            tools.append(store_state_tool)
        if adk_tavily_tool is not None:
            tools.append(adk_tavily_tool)
            
        ActivityAgent = Agent(
            model=MODEL,
            name="activity_agent",
            description=(
                "Recommend activities and attractions based on user preferences and requirements."
            ),
            instruction=PROMPT,
            tools=tools,
            before_model_callback=rate_limit_callback,
        )
        logger.info(f"Activity agent created successfully with {len(tools)} tools")
        
    except ImportError as e:
        logger.error(f"Failed to import ADK components for activity agent: {e}")
        ActivityAgent = None
else:
    logger.info("Direct API Mode: Activity agent not loaded with ADK")
    ActivityAgent = None

# Direct API function for activity search
def activity_tavily_search(query: str, location: str = None, max_results: int = 5):
    """
    Search for travel activities using Tavily search.
    
    Args:
        query: The search query
        location: Location to focus the search on
        max_results: Maximum number of results to return
    
    Returns:
        dict: Search results or None if search failed
    """
    if not TAVILY_AVAILABLE:
        logger.warning("Tavily search not available")
        return None
    
    try:
        results = search_with_tavily(query, location, max_results)
        return results
    except Exception as e:
        logger.error(f"Error in activity_tavily_search: {e}")
        return None
