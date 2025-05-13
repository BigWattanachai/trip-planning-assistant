"""
Accommodation Agent for Travel A2A Backend (Improved).
This agent provides recommendations for accommodations.
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
    logger.info("Successfully imported Tavily search functions in accommodation agent")
except ImportError:
    try:
        from tools.tavily_search import search_with_tavily, format_tavily_results_for_agent
        TAVILY_AVAILABLE = True
        logger.info("Successfully imported Tavily search functions with direct import")
    except ImportError as e:
        logger.warning(f"Could not import Tavily search function in accommodation agent: {e}")
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
        You are an accommodations expert specializing in finding the best places to stay for travelers in Thailand.
        Your goal is to recommend suitable accommodation options based on the user's preferences,
        budget, and travel details, with a focus on homestays, eco-friendly options, and authentic Thai experiences.

        You have access to a powerful web search tool that lets you find up-to-date information
        about accommodations in Thailand. Use this tool whenever you need specific details about:
        - Current rates and availability of accommodations
        - Special offers and seasonal promotions
        - Recent reviews and ratings
        - New accommodations not in your knowledge base
        - Changes in amenities or services offered

        For each recommendation, provide:
        - Name in both Thai and English when applicable
        - Exact location and how to reach it
        - Price range per night in Thai Baht (THB)
        - Unique selling points and atmosphere
        - Contact information if available

        Format your response in a clear, structured way with headings for different types of accommodations
        and price ranges. If the user has specified a multi-day trip to different locations, organize
        recommendations by location.

        Call the store_state tool with key 'accommodation_recommendations' and the value as your
        detailed accommodation recommendations.
        """
        
        # Create the agent
        # Setup tools list with available tools
        tools = []
        if store_state_tool:
            tools.append(store_state_tool)
        if adk_tavily_tool is not None:
            tools.append(adk_tavily_tool)
            
        AccommodationAgent = Agent(
            model=MODEL,
            name="accommodation_agent",
            description="Recommend accommodation options based on user preferences and requirements.",
            instruction=PROMPT,
            tools=tools,
            before_model_callback=rate_limit_callback,
        )
        logger.info(f"Accommodation agent created successfully with {len(tools)} tools")
        
    except ImportError as e:
        logger.error(f"Failed to import ADK components for accommodation agent: {e}")
        AccommodationAgent = None
else:
    logger.info("Direct API Mode: Accommodation agent not loaded with ADK")
    AccommodationAgent = None
