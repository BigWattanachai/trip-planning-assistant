"""
Transportation Agent for Travel A2A Backend (Improved).
This agent provides recommendations for transportation options.
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
    logger.info("Successfully imported Tavily search functions in transportation agent")
except ImportError:
    try:
        from tools.tavily_search import search_with_tavily, format_tavily_results_for_agent
        TAVILY_AVAILABLE = True
        logger.info("Successfully imported Tavily search functions with direct import")
    except ImportError as e:
        logger.warning(f"Could not import Tavily search function in transportation agent: {e}")
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
        You are a transportation expert specializing in helping travelers navigate Thailand's diverse
        transportation systems. Your goal is to recommend suitable transportation options based on the
        user's travel details, with a focus on both efficiency and experiencing the local travel culture.

        You have access to a powerful web search tool that lets you find up-to-date information
        about transportation options in Thailand. Use this tool whenever you need specific details about:
        - Current schedules and timetables for transportation services
        - Fare information and ticket prices
        - Recent changes to routes or services
        - Special transportation options or restrictions
        - Seasonal variations in transportation services

        For each recommendation, provide:
        - Service name in both Thai and English when applicable
        - Departure and arrival points with specific terminal information
        - Schedule information and frequency
        - Fare information in Thai Baht (THB)
        - Booking methods (websites, apps, phone numbers)
        - Comfort level and amenities

        Call the store_state tool with key 'transportation_recommendations' and the value as your
        detailed transportation recommendations.
        """
        
        # Create the agent
        # Setup tools list with available tools
        tools = []
        if store_state_tool:
            tools.append(store_state_tool)
        if adk_tavily_tool is not None:
            tools.append(adk_tavily_tool)
            
        TransportationAgent = Agent(
            model=MODEL,
            name="transportation_agent",
            description="Recommend transportation options based on user travel details.",
            instruction=PROMPT,
            tools=tools,
            before_model_callback=rate_limit_callback,
        )
        logger.info(f"Transportation agent created successfully with {len(tools)} tools")
        
    except ImportError as e:
        logger.error(f"Failed to import ADK components for transportation agent: {e}")
        TransportationAgent = None
else:
    logger.info("Direct API Mode: Transportation agent not loaded with ADK")
    TransportationAgent = None
