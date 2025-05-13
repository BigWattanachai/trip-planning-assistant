"""
YouTube Insight Agent for Travel A2A Backend (Improved).
This agent provides insights and analysis of travel destinations from YouTube content.
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

# Import YouTube tools
try:
    from backend_improve.tools.youtube import (
        search_travel_videos,
        get_video_details,
        extract_travel_insights,
        get_popular_travel_channels,
        get_destination_sentiment
    )
    YOUTUBE_TOOLS_AVAILABLE = True
    logger.info("Successfully imported YouTube tools in YouTube insight agent")
except ImportError:
    try:
        from tools.youtube import (
            search_travel_videos,
            get_video_details,
            extract_travel_insights,
            get_popular_travel_channels,
            get_destination_sentiment
        )
        YOUTUBE_TOOLS_AVAILABLE = True
        logger.info("Successfully imported YouTube tools with direct import")
    except ImportError as e:
        logger.warning(f"Could not import YouTube tools in YouTube insight agent: {e}")
        YOUTUBE_TOOLS_AVAILABLE = False

# Import base tools
try:
    from backend_improve.tools.store_state import store_state_tool
except ImportError:
    try:
        from tools.store_state import store_state_tool
    except ImportError:
        logger.warning("Could not import store_state_tool")
        store_state_tool = None

# Only import ADK components if we're using Vertex AI
if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes"):
    try:
        from google.adk.agents import Agent
        from google.adk.tools import FunctionTool
        
        # Import the model
        try:
            # First try backend-prefix import
            from backend_improve import MODEL
        except (ImportError, ValueError):
            # Fall back to environment variable
            MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")
        
        # Import callbacks
        try:
            from backend_improve.shared_libraries.callbacks import rate_limit_callback
        except (ImportError, ValueError):
            try:
                from shared_libraries.callbacks import rate_limit_callback
            except ImportError as e:
                logger.error(f"Failed to import callbacks: {e}")
                rate_limit_callback = None
        
        # Create function tools for YouTube features
        youtube_tools = []
        
        if YOUTUBE_TOOLS_AVAILABLE:
            # Create ADK function tools for each YouTube function
            search_travel_videos_tool = FunctionTool(
                function=search_travel_videos,
                description="Search for travel-specific YouTube videos about a destination"
            )
            
            get_video_details_tool = FunctionTool(
                function=get_video_details,
                description="Get detailed information about a travel video, including transcript analysis"
            )
            
            extract_travel_insights_tool = FunctionTool(
                function=extract_travel_insights,
                description="Extract travel insights from multiple videos about a destination"
            )
            
            get_popular_travel_channels_tool = FunctionTool(
                function=get_popular_travel_channels,
                description="Find popular YouTube channels that focus on travel content"
            )
            
            get_destination_sentiment_tool = FunctionTool(
                function=get_destination_sentiment,
                description="Analyze YouTube content sentiment about a travel destination"
            )
            
            # Add tools to list
            youtube_tools.extend([
                search_travel_videos_tool,
                get_video_details_tool,
                extract_travel_insights_tool,
                get_popular_travel_channels_tool,
                get_destination_sentiment_tool
            ])
            
            logger.info(f"Created {len(youtube_tools)} YouTube function tools")
        
        # Create the agent instruction prompt
        PROMPT = """
        You are a YouTube Travel Insight Agent that specializes in extracting and analyzing travel information 
        from YouTube videos. Your goal is to help travelers by providing insights about destinations based on 
        YouTube content.
        
        You have access to specialized tools that can:
        1. Search for travel videos about specific destinations
        2. Extract detailed information from travel videos, including transcript analysis
        3. Find popular travel channels that focus on specific destinations or travel styles
        4. Analyze sentiment about destinations from YouTube content
        5. Extract aggregate insights from multiple videos about a destination
        
        For any destination questions, use your tools to search for relevant videos and extract insights to 
        provide the most current and accurate information. Focus particularly on:
        - Popular attractions and places mentioned in multiple videos
        - Common activities and experiences recommended by travel content creators
        - Sentiment about destinations (positive/negative aspects)
        - Travel tips and recommendations mentioned in videos
        
        When providing information:
        - Always cite video sources by title and channel name
        - Highlight when information comes from multiple sources for greater reliability
        - Be transparent about the limitations of your analysis
        - Organize information in a clear, structured format
        - Provide a balanced perspective, including both positive and negative aspects
        
        If the user asks about a destination, make sure to:
        1. Search for recent videos about that destination
        2. Get detailed information from the most relevant videos
        3. Extract insights from multiple videos for more reliable information
        4. Analyze sentiment to understand how the destination is generally portrayed
        5. Recommend specific YouTube channels that focus on that destination if available
        
        Call the store_state tool with key 'youtube_insights' and the value as your detailed insights
        to save the information for other agents.
        """
        
        # Create tools list with available tools
        tools = youtube_tools.copy()
        if store_state_tool:
            tools.append(store_state_tool)
        
        # Create the YouTube Insight Agent
        YouTubeInsightAgent = Agent(
            model=MODEL,
            name="youtube_insight_agent",
            description="Provides insights and analysis of travel destinations from YouTube content",
            instruction=PROMPT,
            tools=tools,
            before_model_callback=rate_limit_callback,
        )
        
        logger.info(f"YouTube Insight agent created successfully with {len(tools)} tools")
        
    except ImportError as e:
        logger.error(f"Failed to import ADK components for YouTube insight agent: {e}")
        YouTubeInsightAgent = None
else:
    logger.info("Direct API Mode: YouTube Insight agent not loaded with ADK")
    YouTubeInsightAgent = None

# Direct API functions for YouTube insights
def search_youtube_travel_content(destination: str, content_type: str = "travel guide") -> dict:
    """
    Search for travel content on YouTube.
    
    Args:
        destination: The destination to search for
        content_type: Type of content to search for (default: "travel guide")
    
    Returns:
        dict: Search results or error message
    """
    if not YOUTUBE_TOOLS_AVAILABLE:
        logger.warning("YouTube tools not available")
        return {"error": "YouTube tools not available"}
    
    try:
        results = search_travel_videos(destination, content_type)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error in search_youtube_travel_content: {e}")
        return {"error": str(e)}

def analyze_destination_from_youtube(destination: str) -> dict:
    """
    Analyze a destination based on YouTube content.
    
    Args:
        destination: The destination to analyze
    
    Returns:
        dict: Analysis results or error message
    """
    if not YOUTUBE_TOOLS_AVAILABLE:
        logger.warning("YouTube tools not available")
        return {"error": "YouTube tools not available"}
    
    try:
        # First search for videos about the destination
        videos = search_travel_videos(destination, "travel guide")
        
        if not videos or "error" in videos[0]:
            return {"error": f"Could not find videos for {destination}"}
        
        # Get video IDs from search results
        video_ids = [video["id"] for video in videos[:5]]
        
        # Extract insights from the videos
        insights = extract_travel_insights(video_ids)
        
        # Get sentiment analysis
        sentiment = get_destination_sentiment(destination)
        
        # Get popular channels
        channels = get_popular_travel_channels(f"{destination} travel")
        
        # Combine all results
        return {
            "destination": destination,
            "insights": insights,
            "sentiment": sentiment,
            "channels": channels,
            "videos": videos[:5]
        }
    except Exception as e:
        logger.error(f"Error in analyze_destination_from_youtube: {e}")
        return {"error": str(e)}
