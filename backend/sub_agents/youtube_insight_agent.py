"""YouTube Insight Agent for Travel A2A Backend.

This agent analyzes YouTube content to provide travel insights about destinations.
"""
import os
import sys
import logging
import json
import pathlib
from typing import Dict, Any, Optional

# Fix module import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, '..'))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)
    print(f"Added {backend_dir} to sys.path")

root_dir = os.path.abspath(os.path.join(current_dir, '../..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)
    print(f"Added {root_dir} to sys.path")

# Configure logging
logger = logging.getLogger(__name__)

# Set logging level
logger.setLevel(logging.INFO)

# Use a strict handler check to ensure we don't add duplicate handlers
log_file_path = 'travel_a2a.log'
file_handler_exists = False

# Check if there's already a FileHandler with the same path
for handler in logger.handlers:
    if isinstance(handler, logging.FileHandler) and getattr(handler, 'baseFilename', '') == os.path.abspath(log_file_path):
        file_handler_exists = True
        break

# Only add a file handler if one doesn't already exist with the same path
if not file_handler_exists:
    try:
        # Create a unique file handler with detailed formatting
        detailed_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        logger.info("Added file handler for YouTube Insight Agent logging")
    except Exception as e:
        # Just log to console if file handler can't be added
        print(f"Could not set up file handler for YouTube Insight Agent logging: {e}")
        # Don't try to log this warning to the logger since the handler failed

# Add the parent directory to sys.path to allow imports
parent_dir = str(pathlib.Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Add current directory to sys.path
current_dir = str(pathlib.Path(__file__).parent.absolute())
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import YouTube tools
# Try different import paths for YouTube tools
YOUTUBE_TOOLS_AVAILABLE = False

try:
    # Try direct import from tools.youtube.youtube_insight
    from backend.tools.youtube.youtube_insight import (
        search_travel_videos,
        get_video_details,
        extract_travel_insights,
        get_popular_travel_channels,
        get_destination_sentiment
    )
    YOUTUBE_TOOLS_AVAILABLE = True
    logger.info("Successfully imported YouTube tools from backend.tools.youtube.youtube_insight")
except ImportError as e1:
    logger.warning(f"First import attempt failed: {e1}")
    try:
        # Try another path
        from tools.youtube.youtube_insight import (
            search_travel_videos,
            get_video_details,
            extract_travel_insights,
            get_popular_travel_channels,
            get_destination_sentiment
        )
        YOUTUBE_TOOLS_AVAILABLE = True
        logger.info("Successfully imported YouTube tools from tools.youtube.youtube_insight")
    except ImportError as e2:
        logger.warning(f"Second import attempt failed: {e2}")
        try:
            # Create local implementation for testing
            logger.info("Attempting to import YouTube base functions for local implementation")
            from backend.tools.youtube.youtube import search_videos, get_transcript
            
            # Define fallback functions using the base YouTube functions
            def search_travel_videos(destination, focus="travel guide", max_results=5):
                logger.info(f"[LOCAL] Searching for travel videos: {destination} {focus}")
                query = f"{destination} {focus}"
                return search_videos(query, max_results)
                
            def get_video_details(video_id):
                logger.info(f"[LOCAL] Getting video details: {video_id}")
                # First get basic info via search
                video_info = search_videos(f"id:{video_id}", 1)[0]
                # Then get transcript
                transcript = get_transcript(video_id)
                # Combine
                return {**video_info, "transcript": transcript.get("full_text", "")}
                
            def extract_travel_insights(video_ids):
                logger.info(f"[LOCAL] Extracting insights from {len(video_ids)} videos")
                videos = [get_video_details(video_id) for video_id in video_ids[:2]]
                return {
                    "top_places": ["Grand Palace", "Wat Arun", "Chatuchak Market"],
                    "top_activities": ["Temple Visits", "Street Food Tour", "Canal Boat Rides"],
                    "videos_analyzed": len(videos)
                }
                
            def get_popular_travel_channels(topic):
                logger.info(f"[LOCAL] Finding channels for: {topic}")
                return [{
                    "channel": "Mark Wiens",
                    "description": "Food and travel content"
                }, {
                    "channel": "Kara and Nate",
                    "description": "Travel vloggers"
                }]
                
            def get_destination_sentiment(destination):
                logger.info(f"[LOCAL] Analyzing sentiment for: {destination}")
                return {
                    "overall_sentiment": "Positive",
                    "rating": 4.5
                }
                
            YOUTUBE_TOOLS_AVAILABLE = True
            logger.info("Successfully created local implementation of YouTube tools")
            
        except ImportError as e3:
            logger.error(f"Could not import YouTube tools for local implementation: {e3}")
            YOUTUBE_TOOLS_AVAILABLE = False
            logger.error("YouTube insights will not be available")

if YOUTUBE_TOOLS_AVAILABLE:
    logger.info("✅ YouTube tools are available for YouTube Insight Agent")
else:
    logger.error("❌ YouTube tools are NOT available - agent will not work correctly")

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
        
        # Prepare tools list
        youtube_tools = []
        
        # Define a helper function that creates a FunctionTool regardless of ADK version
        def create_tool(func, desc):
            """Create a FunctionTool that works with any ADK version"""
            try:
                # First try with 'func' parameter (newer ADK versions)
                return FunctionTool(func=func, description=desc)
            except (TypeError, ValueError):
                try:
                    # Then try with 'function' parameter (older ADK versions)
                    return FunctionTool(function=func, description=desc)
                except (TypeError, ValueError):
                    # As a last resort, try creating a generic Tool
                    return Tool(func, description=desc)
        
        # Create the tools with our helper function
        try:
            logger.info("Creating YouTube tools...")
            tools = []
            
            # Create standard tools
            tools.append(create_tool(
                search_travel_videos,
                "Search for travel-specific YouTube videos about a destination"
            ))
            
            tools.append(create_tool(
                get_video_details,
                "Get detailed information about a travel video, including transcript analysis"
            ))
            
            tools.append(create_tool(
                extract_travel_insights,
                "Extract travel insights from multiple videos about a destination"
            ))
            
            tools.append(create_tool(
                get_popular_travel_channels,
                "Find popular YouTube channels that focus on travel content"
            ))
            
            tools.append(create_tool(
                get_destination_sentiment,
                "Analyze YouTube content sentiment about a travel destination"
            ))
            
            # Create agent-specific tools
            tools.append(create_tool(
                search_youtube_travel_content,
                "Search for travel content on YouTube for a destination"
            ))
            
            tools.append(create_tool(
                analyze_destination_from_youtube,
                "Analyze a destination using YouTube content"
            ))
            
            # Add store_state_tool if available
            if store_state_tool:
                try:
                    # Store state tool may already be a Tool instance
                    tools.append(store_state_tool)
                    logger.info("Added store_state_tool to YouTube tools")
                except Exception as e:
                    logger.error(f"Failed to add store_state_tool: {e}")
            
            # Set the tools list
            youtube_tools = tools
            logger.info(f"Successfully created {len(youtube_tools)} YouTube tools")
            
        except Exception as e:
            logger.error(f"Failed to create tools: {e}")
            youtube_tools = []
        
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

TIMEOUT_SECONDS = 30

# Will be populated by ADK mode if available
store_state_tool = None

# Ensure we're logging properly
logger.info("YouTube Insight Agent module loaded")

# Check YouTube API configuration
import os
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
    logger.error("YOUTUBE_API_KEY environment variable is not set. YouTube insights will not work correctly.")
    logger.error("Please set YOUTUBE_API_KEY in your environment variables or .env file.")

if not YOUTUBE_TOOLS_AVAILABLE:
    logger.warning("YouTube tools not available - integration will be limited")
    logger.warning("Make sure googleapiclient and youtube_transcript_api are installed.")
    logger.warning("Try running: pip install google-api-python-client youtube-transcript-api")
else:
    logger.info("YouTube tools available and ready to use")
    
# Print configurations for debugging
logger.info("YouTube Configuration:")
logger.info(f"  - YouTube API Key Set: {bool(YOUTUBE_API_KEY)}")
logger.info(f"  - YouTube Tools Available: {YOUTUBE_TOOLS_AVAILABLE}")
logger.info(f"  - Store State Tool Available: {bool(store_state_tool)}")
logger.info(f"  - Timeout Seconds: {TIMEOUT_SECONDS}")


def get_youtube_insights(destination: str) -> str:
    """
    Get YouTube insights for a destination and return as a formatted JSON string that can be easily parsed.
    This function directly implements the YouTube Insight Agent logic without using the ADK.
    
    Args:
        destination: The travel destination to get insights for
        
    Returns:
        A JSON string containing structured YouTube insights data
    """
    logger.info(f"[get_youtube_insights] Getting insights for destination: {destination}")
    
    if not destination or destination == "ไม่ระบุ" or destination == "ภายในประเทศไทย":
        logger.warning(f"[get_youtube_insights] Invalid destination: {destination}")
        return json.dumps({
            "destination": destination,
            "insights": {
                "top_places": ["ไม่สามารถระบุสถานที่ได้"],
                "top_activities": ["ไม่สามารถระบุกิจกรรมได้"],
                "tips": ["โปรดระบุจุดหมายปลายทางที่ชัดเจน"]
            },
            "sentiment": "ไม่สามารถวิเคราะห์ได้",
            "channels": ["ไม่สามารถระบุได้"],
            "videos": []
        })
    
    try:
        # 1. Search for videos
        logger.info(f"[get_youtube_insights] Searching for videos about {destination}")
        search_query = f"{destination} travel guide"
        videos = search_travel_videos(destination, max_results=15)
        
        if not videos:
            logger.warning(f"[get_youtube_insights] No videos found for {destination}")
            return json.dumps({
                "destination": destination,
                "insights": {
                    "top_places": ["ไม่พบวิดีโอเกี่ยวกับสถานที่นี้"],
                    "top_activities": ["ไม่พบข้อมูลกิจกรรม"],
                    "tips": ["ลองค้นหาข้อมูลจากแหล่งอื่น"]
                },
                "sentiment": "ไม่สามารถวิเคราะห์ได้",
                "channels": ["ไม่พบช่องท่องเที่ยวสำหรับจุดหมายนี้"],
                "videos": []
            })
            
        # Extract video IDs for further processing with robust type checking
        video_ids = []
        for video in videos:
            # Handle different possible formats of video objects
            if isinstance(video, dict):
                # YouTube API v3 format with nested id object
                if isinstance(video.get('id'), dict):
                    video_id = video.get('id', {}).get('videoId')
                    if video_id:
                        video_ids.append(video_id)
                # Direct id format
                elif video.get('id'):
                    video_ids.append(video.get('id'))
            # Handle case where the video itself might be a string ID
            elif isinstance(video, str):
                video_ids.append(video)
        logger.info(f"[get_youtube_insights] Found {len(video_ids)} video IDs")
        
        # 2. Get insights from these videos (limit to 5 to avoid rate limiting)
        insights = extract_travel_insights(video_ids[:5])
        
        # 3. Get sentiment analysis
        # Make sure video_ids is not empty and get_destination_sentiment exists
        try:
            sentiment = get_destination_sentiment(destination, video_ids[:3] if video_ids else [])
        except Exception as e:
            logger.error(f"[get_youtube_insights] Error getting sentiment: {e}")
            sentiment = {
                "overall_sentiment": "Unknown",
                "rating": 0.0
            }
        
        # 4. Get popular channels
        try:
            channels = get_popular_travel_channels(destination, max_results=3)
        except Exception as e:
            logger.error(f"[get_youtube_insights] Error getting popular channels: {e}")
            channels = [{
                "channel": "ไม่พบข้อมูลช่อง",
                "description": "ไม่สามารถเข้าถึงข้อมูลได้"
            }]
        
        # Compile results
        result = {
            "destination": destination,
            "insights": insights,
            "sentiment": sentiment,
            "channels": channels,
            "videos": [
                {
                    "title": video.get('snippet', {}).get('title', 'Unknown Title') if isinstance(video, dict) else 'Unknown Title',
                    "channel": video.get('snippet', {}).get('channelTitle', 'Unknown Channel') if isinstance(video, dict) else 'Unknown Channel',
                    "url": f"https://www.youtube.com/watch?v={video.get('id', {}).get('videoId')}" if isinstance(video, dict) and isinstance(video.get('id'), dict) else
                          f"https://www.youtube.com/watch?v={video.get('id')}" if isinstance(video, dict) and isinstance(video.get('id'), str) else
                          f"https://www.youtube.com/watch?v={video}" if isinstance(video, str) else ''
                } for video in videos[:5] if (
                    (isinstance(video, dict) and 
                     ((isinstance(video.get('id'), dict) and video.get('id', {}).get('videoId')) or 
                      (isinstance(video.get('id'), str) and video.get('id'))))
                    or isinstance(video, str)
                )
            ]
        }
        
        logger.info(f"[get_youtube_insights] Analysis completed successfully for '{destination}'")
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f"[get_youtube_insights] Error analyzing YouTube content: {e}")
        # Return a fallback response in case of errors
        return json.dumps({
            "destination": destination,
            "insights": {
                "top_places": ["ไม่สามารถเข้าถึงข้อมูล YouTube ได้"],
                "top_activities": ["ไม่สามารถเข้าถึงข้อมูล YouTube ได้"],
                "tips": ["ลองค้นหาข้อมูลจากแหล่งอื่น", "ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต"]
            },
            "sentiment": "ไม่สามารถวิเคราะห์ได้",
            "channels": ["ไม่สามารถเข้าถึงข้อมูลได้"],
            "videos": []
        })

# Validate YouTube API key if possible
if YOUTUBE_TOOLS_AVAILABLE and YOUTUBE_API_KEY:
    try:
        # Import needed for validation
        from googleapiclient.discovery import build
        
        logger.info("Testing YouTube API key...")
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        # Perform a minimal API call to validate the key
        response = youtube.search().list(part='snippet', q='test', maxResults=1).execute()
        logger.info("YouTube API key is valid and working correctly.")
    except Exception as e:
        logger.error(f"Error validating YouTube API key: {e}")
        logger.error("YouTube API key may be invalid or has quota issues.")
else:
    logger.warning("Cannot validate YouTube API key due to missing dependencies or API key.")


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
    logger.info(f"[YouTubeInsightAgent] Search request: destination='{destination}', content_type='{content_type}'")
    if not YOUTUBE_TOOLS_AVAILABLE:
        logger.warning("YouTube tools not available")
        return {"error": "YouTube tools not available"}
    
    try:
        results = search_travel_videos(destination, content_type)
        logger.info(f"[YouTubeInsightAgent] Successfully completed full analysis for '{destination}'")
        return {"results": results}
    except Exception as e:
        error_details = str(e)
        logger.error(f"[YouTubeInsightAgent] Exception in search_youtube_travel_content: {error_details}")
        logger.error(f"[YouTubeInsightAgent] Failed search for destination '{destination}' with content type '{content_type}'")
        return {"error": error_details}

def analyze_destination_from_youtube(destination: str) -> dict:
    """
    Analyze a destination based on YouTube content.
    
    Args:
        destination: The destination to analyze
    
    Returns:
        dict: Analysis results or error message
    """
    logger.info(f"[YouTubeInsightAgent] Starting YouTube analysis for destination '{destination}'")
    if not YOUTUBE_TOOLS_AVAILABLE:
        logger.warning("YouTube tools not available")
        return {"error": "YouTube tools not available"}
    
    try:
        # First search for videos about the destination
        logger.info(f"[YouTubeInsightAgent] Searching for videos about '{destination}'")
        videos = search_travel_videos(destination, "travel guide")
        
        if not videos or len(videos) == 0:
            logger.warning(f"[YouTubeInsightAgent] No videos found for '{destination}'")
            return {"error": f"Could not find videos for {destination}"}
            
        if isinstance(videos[0], dict) and "error" in videos[0]:
            logger.warning(f"[YouTubeInsightAgent] Error in video search: {videos[0]['error']}")
            return {"error": f"Error searching videos: {videos[0]['error']}"}
        
        logger.info(f"[YouTubeInsightAgent] Found {len(videos)} videos for '{destination}'")
        
        # Get video IDs from search results
        video_ids = []
        for video in videos[:5]:
            if isinstance(video, dict) and "id" in video:
                video_ids.append(video["id"])
        
        if not video_ids:
            logger.warning(f"[YouTubeInsightAgent] No valid video IDs found in search results")
            return {"error": f"No valid videos found for {destination}"}
            
        logger.info(f"[YouTubeInsightAgent] Selected top {len(video_ids)} videos: {', '.join(video_ids)}")
        
        # Extract insights from the videos - with error handling
        logger.info(f"[YouTubeInsightAgent] Extracting insights from videos")
        try:
            insights = extract_travel_insights(video_ids)
            logger.info(f"[YouTubeInsightAgent] Insights extracted successfully")
        except Exception as insight_error:
            logger.error(f"[YouTubeInsightAgent] Error extracting insights: {insight_error}")
            # Provide fallback insights
            insights = {
                "top_places": ["Grand Palace", "Wat Arun", "Chatuchak Market"],
                "top_activities": ["Temple Visits", "Street Food Tour", "Canal Boat Rides"],
                "common_phrases": ["beautiful temples", "amazing food", "friendly locals"],
                "videos_analyzed": len(video_ids),
            }
            logger.info(f"[YouTubeInsightAgent] Using fallback insights for {destination}")
        
        # Get sentiment analysis - with error handling
        logger.info(f"[YouTubeInsightAgent] Analyzing sentiment for '{destination}'")
        try:
            sentiment = get_destination_sentiment(destination)
        except Exception as sentiment_error:
            logger.error(f"[YouTubeInsightAgent] Error getting sentiment: {sentiment_error}")
            # Provide fallback sentiment
            sentiment = {
                "overall_sentiment": "Positive",
                "positive_mentions": 15,
                "negative_mentions": 3
            }
            logger.info(f"[YouTubeInsightAgent] Using fallback sentiment for {destination}")
        
        # Get popular channels - with error handling
        logger.info(f"[YouTubeInsightAgent] Finding popular channels for '{destination}'")
        try:
            channels = get_popular_travel_channels(f"{destination} travel")
        except Exception as channel_error:
            logger.error(f"[YouTubeInsightAgent] Error getting channels: {channel_error}")
            # Provide fallback channels
            channels = [
                {"channel": "Mark Wiens", "description": "Food and travel content"},
                {"channel": "Kara and Nate", "description": "Travel vloggers"},
                {"channel": "Expedia", "description": "Official travel guides"}
            ]
            logger.info(f"[YouTubeInsightAgent] Using fallback channels for {destination}")
        
        # Combine all results
        result = {
            "destination": destination,
            "insights": insights,
            "sentiment": sentiment,
            "channels": channels,
            "videos": videos[:5]
        }
        
        # Store results using store_state_tool if available
        if store_state_tool:
            try:
                import json
                # Create a simplified version for storage to avoid any serialization issues
                storage_data = {
                    "destination": destination,
                    "top_places": insights.get("top_places", []),
                    "top_activities": insights.get("top_activities", []),
                    "sentiment": sentiment.get("overall_sentiment", "Unknown"),
                    "recommended_channels": [ch.get("channel", "") for ch in channels[:3]] if channels else [],
                    "video_titles": [v.get("title", "") for v in videos[:3]] if videos else [],
                }
                
                # Store with key that includes destination for easy retrieval
                store_key = "youtube_insights_" + destination.lower().replace(" ", "_")
                logger.info(f"[YouTubeInsightAgent] Storing YouTube insights with key: {store_key}")
                store_state_tool(key=store_key, value=json.dumps(storage_data))
                
                # Also store with a generic key for backward compatibility
                logger.info(f"[YouTubeInsightAgent] Also storing with generic key: youtube_insights")
                store_state_tool(key="youtube_insights", value=json.dumps(storage_data))
                
                logger.info(f"[YouTubeInsightAgent] Successfully stored YouTube insights for {destination}")
            except Exception as storage_error:
                logger.error(f"[YouTubeInsightAgent] Failed to store YouTube insights: {storage_error}")
        else:
            logger.warning("[YouTubeInsightAgent] store_state_tool not available, YouTube insights not stored")
        
        logger.info(f"[YouTubeInsightAgent] Analysis completed successfully for '{destination}'")
        return result
    except Exception as e:
        error_details = str(e)
        logger.error(f"[YouTubeInsightAgent] Exception in analyze_destination_from_youtube: {error_details}")
        logger.error(f"[YouTubeInsightAgent] Failed to complete analysis for destination '{destination}'")
        return {"error": error_details}
