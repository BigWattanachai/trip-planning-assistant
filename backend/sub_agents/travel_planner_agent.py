"""
Travel Planner Agent for Travel A2A Backend (Improved).
This agent creates comprehensive travel plans based on sub-agent inputs.
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
    logger.info("Successfully imported Tavily search functions in travel planner agent")
except ImportError:
    try:
        from tools.tavily_search import search_with_tavily, format_tavily_results_for_agent
        TAVILY_AVAILABLE = True
        logger.info("Successfully imported Tavily search functions with direct import")
    except ImportError as e:
        logger.warning(f"Could not import Tavily search function in travel planner agent: {e}")
        TAVILY_AVAILABLE = False

# Only import ADK components if we're using Vertex AI
if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes"):
    try:
        from google.adk.agents import Agent
        from google.adk.tools.langchain_tool import LangchainTool
        
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
        You are a Thailand travel planner expert specializing in creating comprehensive, authentic travel itineraries.
        Your goal is to take the recommendations from the transportation, accommodation, restaurant,
        and activity agents and combine them into a cohesive day-by-day travel plan that emphasizes
        nature-focused experiences, local culture, and authentic Thai cuisine.

        You have access to a powerful web search tool that lets you find up-to-date information
        about destinations, events, weather forecasts, and more. Use this tool whenever you need specific details about:
        - Current events or festivals during the planned travel dates
        - Seasonal weather patterns that might affect activities
        - Recent changes to operating hours or policies
        - Travel advisories or local regulations
        - Recommended itineraries based on the time of year

        Create a day-by-day itinerary that:
        - Logically sequences activities, meals, and transportation based on proximity and timing
        - Balances active experiences with relaxation time
        - Incorporates both must-see attractions and off-the-beaten-path experiences
        - Allows for flexibility and spontaneity
        - Considers weather patterns and seasonal factors

        Format the plan for maximum usability:
        - Clear day-by-day structure with timestamps
        - Maps or directions between locations when relevant
        - Contact information for recommended services
        - Meal suggestions with timing and location
        - Clearly marked free time periods

        Call the store_state tool with key 'travel_plan' and the value as your comprehensive travel plan.

        Your final plan should be detailed but readable, with a clear structure that makes it easy for
        the traveler to follow. Use headings, bullet points, and a logical organization to create a
        practical, enjoyable experience that authentically connects travelers with Thai culture,
        nature, and cuisine.

        Format your response with a clear header "===== แผนการเดินทางของคุณ =====" at the beginning.
        """
        
        # Create the agent
        # Setup tools list with available tools
        tools = []
        if store_state_tool:
            tools.append(store_state_tool)
        if adk_tavily_tool is not None:
            tools.append(adk_tavily_tool)
            
        TravelPlannerAgent = Agent(
            model=MODEL,
            name="travel_planner_agent",
            description="Create comprehensive travel plans based on recommendations from specialized agents.",
            instruction=PROMPT,
            tools=tools,
            before_model_callback=rate_limit_callback,
        )
        logger.info(f"Travel planner agent created successfully with {len(tools)} tools")
        
    except ImportError as e:
        logger.error(f"Failed to import ADK components for travel planner agent: {e}")
        TravelPlannerAgent = None
else:
    logger.info("Direct API Mode: Travel planner agent not loaded with ADK")
    TravelPlannerAgent = None
