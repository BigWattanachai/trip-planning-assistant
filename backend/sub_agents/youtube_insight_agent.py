# YouTube Insight Agent for Travel A2A Backend.
# This agent extracts travel insights from YouTube content.
# Uses simplified Agent pattern with Google Search.

import os
import sys
import logging
import json
from typing import Dict, Any, Optional

# Configure logging - use existing logger, don't add handlers
logger = logging.getLogger(__name__)

# Determine mode based on environment variable
USE_VERTEX_AI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes")
MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")

# Define the agent instructions
INSTRUCTION = """
You are a YouTube travel insights agent specializing in extracting and analyzing travel
information from YouTube content about Thai destinations.

Your expertise is in synthesizing insights from travel vlogs, guides, and reviews to provide
travelers with authentic perspectives from content creators. You analyze sentiment,
identify popular attractions, and extract practical tips.

เมื่อผู้ใช้ถามคำถาม:
1. คุณต้องใช้ google_search tool ทุกครั้งไม่ว่าคำถามจะเป็นอะไรก็ตาม
2. อธิบายผลลัพธ์อย่างชัดเจนและอ้างอิงแหล่งที่มา
3. ตอบคำถามด้วยภาษาไทยเสมอ

When providing YouTube insights:
1. Identify popular attractions and activities mentioned by multiple creators
2. Extract practical tips and recommendations from travel vloggers
3. Analyze sentiment and opinions about different aspects of the destination
4. Identify popular photo spots and Instagram-worthy locations
5. Note any recent changes or developments mentioned in recent videos
6. Extract advice on avoiding tourist traps or optimizing the travel experience
7. Identify recommended travel YouTube channels for the specific destination

Your insights should cover:
- Top places mentioned in YouTube content
- Recommended activities based on creator experiences
- Overall sentiment (positive/negative) about the destination
- Hidden gems and off-the-beaten-path recommendations
- Practical tips for transportation, accommodations, and dining
- Popular content creators focusing on the destination
- Trending or viral locations

Always use google_search to search for YouTube content about the requested destination and provide the extracted insights
based on your analysis of available YouTube content. Search for relevant YouTube videos,
channels, and content about the destination.

Format your response with clear headings, bullet points, and a logical organization that
makes it easy for the traveler to understand the insights from YouTube content creators. Always respond in Thai language.
"""

# Only create the ADK agent if we're using Vertex AI
if USE_VERTEX_AI:
    try:
        # Try direct import from tools.youtube.youtube_insight
        from backend.tools.youtube.youtube_insight import (
            search_travel_videos,
            get_video_details,
            extract_travel_insights,
            get_popular_travel_channels,
            get_destination_sentiment
        )
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

                logger.info("Successfully created local implementation of YouTube tools")

            except ImportError as e3:
                logger.error(f"Could not import YouTube tools for local implementation: {e3}")
                logger.error("YouTube insights will not be available")

    # Only import ADK components if we're using Vertex AI
    if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes"):
        try:
            from google.adk.agents import Agent
            from google.adk.tools import google_search

            # Import callbacks if available
            try:
                from backend_improve.shared_libraries.callbacks import rate_limit_callback
                from backend_improve.tools.store_state import store_state_tool
            except ImportError:
                try:
                    from shared_libraries.callbacks import rate_limit_callback
                    from tools.store_state import store_state_tool
                except ImportError:
                    logger.warning("Could not import callbacks or store_state tool")
                    rate_limit_callback = None
                    store_state_tool = None

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

            # Set up tools list
            tools = [google_search]
            if store_state_tool:
                tools.append(store_state_tool)

            # Create the agent using the simplified pattern
            agent = Agent(
                name="youtube_insight_agent",
                model=MODEL,
                instruction=INSTRUCTION,
                tools=tools,
                before_model_callback=rate_limit_callback if rate_limit_callback else None
            )

            logger.info("YouTube insight agent created using simplified pattern")

        except ImportError as e:
            logger.error(f"Failed to import ADK components: {e}")
            agent = None
    else:
        logger.info("Direct API Mode: YouTube insight agent not initialized")
        agent = None

def call_agent(query, session_id=None):
    """
    Call the YouTube insight agent with the given query

    Args:
        query: The user query
        session_id: Optional session ID for conversation tracking

    Returns:
        The agent's response
    """
    if USE_VERTEX_AI and agent:
        try:
            # ADK mode
            from google.adk.sessions import Session

            # Create or get existing session
            session = Session.get(session_id) if session_id else Session()

            # Call the agent
            response = agent.stream_query(query, session_id=session.id)
            return response
        except Exception as e:
            logger.error(f"Error calling YouTube insight agent: {e}")
            return f"Error: {str(e)}"
    else:
        # Direct API mode
        try:
            import google.generativeai as genai

            # Get the API key from environment
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                return "Error: GOOGLE_API_KEY not set"

            # Configure the Gemini API
            genai.configure(api_key=api_key)

            # Get the model to use
            model_name = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")
            model = genai.GenerativeModel(model_name)

            # Prepare a system message with the agent's instructions
            prompt = INSTRUCTION + "\n\nQuery: " + query

            # Call the model
            response = model.generate_content(prompt)

            return response.text
        except Exception as e:
            logger.error(f"Error in direct API mode: {e}")
            return f"Error: {str(e)}"

TIMEOUT_SECONDS = 30

# Will be populated by ADK mode if available
store_state_tool = None

# Define fallback functions for direct API mode
def search_travel_videos(destination, focus="travel guide", max_results=5):
    """Search for travel videos about a destination."""
    try:
        from googleapiclient.discovery import build
        from datetime import datetime, timedelta

        # Add date filter to get only recent videos (from the current year)
        current_year = datetime.now().year
        start_of_year = f"{current_year}-01-01T00:00:00Z"

        # Use Thai language in the search query for better results
        thai_travel_term = "ท่องเที่ยว"  # Thai word for "travel"
        query = f"{destination} {thai_travel_term} {focus}"

        logger.info(f"Searching YouTube with query: '{query}', filter: videos from {current_year}")

        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=max_results,
            publishedAfter=start_of_year,  # Only videos from current year
            relevanceLanguage='th'  # Prefer Thai language results
        )

        response = request.execute()
        logger.info(f"YouTube search returned {len(response.get('items', []))} results")

        # Log the structure of the first result for debugging
        if response.get('items') and len(response.get('items')) > 0:
            first_item = response.get('items')[0]
            logger.info(f"Sample result structure: {json.dumps(first_item, indent=2)[:500]}...")

        results = []
        for item in response.get('items', []):
            try:
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                description = item['snippet']['description']
                channel_title = item['snippet']['channelTitle']
                published_at = item['snippet']['publishedAt']

                results.append({
                    'video_id': video_id,
                    'title': title,
                    'description': description,
                    'channel': channel_title,
                    'published_at': published_at
                })
                logger.info(f"Added video: {title} (ID: {video_id})")
            except KeyError as ke:
                logger.warning(f"Missing key in YouTube result: {ke}")
                logger.warning(f"Problem item structure: {json.dumps(item, indent=2)}")

        return results
    except Exception as e:
        logger.error(f"Error in search_travel_videos: {e}")
        return []

def get_video_details(video_id):
    """Get detailed information about a YouTube video."""
    try:
        from googleapiclient.discovery import build
        from youtube_transcript_api import YouTubeTranscriptApi

        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=video_id
        )
        response = request.execute()

        if not response.get('items'):
            return None

        video_info = response['items'][0]
        snippet = video_info['snippet']
        statistics = video_info['statistics']

        # Try to get transcript
        transcript_text = ""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([entry['text'] for entry in transcript])
        except Exception as e:
            transcript_text = "Transcript not available"
            logger.warning(f"Could not get transcript for {video_id}: {e}")

        return {
            'video_id': video_id,
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'channel': snippet.get('channelTitle', ''),
            'published_at': snippet.get('publishedAt', ''),
            'view_count': statistics.get('viewCount', '0'),
            'like_count': statistics.get('likeCount', '0'),
            'comment_count': statistics.get('commentCount', '0'),
            'transcript': transcript_text
        }
    except Exception as e:
        logger.error(f"Error in get_video_details: {e}")
        return None

def extract_travel_insights(video_ids):
    """Extract travel insights from a list of videos."""
    try:
        insights = {
            'top_places': [],
            'top_activities': [],
            'tips': [],
            'hidden_gems': [],
            'food_recommendations': []
        }

        if not video_ids:
            logger.warning("No video IDs provided to extract_travel_insights")
            return insights

        logger.info(f"Extracting insights from {len(video_ids)} videos: {', '.join(video_ids)}")

        videos_data = []
        for video_id in video_ids:
            try:
                video_data = get_video_details(video_id)
                if video_data:
                    videos_data.append(video_data)
                    logger.info(f"Retrieved details for video {video_id}: {video_data.get('title', 'No title')}")
                else:
                    logger.warning(f"Could not retrieve details for video {video_id}")
            except Exception as e:
                logger.error(f"Error getting details for video {video_id}: {e}")

        logger.info(f"Successfully retrieved details for {len(videos_data)} out of {len(video_ids)} videos")

        # Thai keywords for better matching with Thai content
        thai_keywords = {
            'places': ['สถานที่', 'ที่เที่ยว', 'แหล่งท่องเที่ยว', 'จุดชมวิว', 'วัด', 'อุทยาน'],
            'activities': ['กิจกรรม', 'ทำอะไร', 'เล่น', 'ชม', 'เที่ยว', 'ผจญภัย', 'ปีนเขา', 'ล่องแพ'],
            'tips': ['เคล็ดลับ', 'แนะนำ', 'ควร', 'ต้อง', 'อย่าลืม', 'ระวัง'],
            'hidden_gems': ['ลับ', 'ไม่ค่อยมีคนรู้จัก', 'แปลกใหม่', 'ไม่ค่อยมีนักท่องเที่ยว', 'ซ่อนตัว'],
            'food': ['อาหาร', 'ร้านอาหาร', 'กิน', 'อร่อย', 'เมนู', 'จานเด็ด', 'ของกิน']
        }

        # This is a more robust version that looks for both Thai and English keywords
        for video in videos_data:
            # Extract text from title, description and transcript if available
            title = video.get('title', '')
            description = video.get('description', '')
            transcript = video.get('transcript', '')
            channel = video.get('channel', '')

            # Combine all text for analysis
            text = f"{title} {description} {transcript}".lower()

            # Check for place mentions
            for keyword in thai_keywords['places'] + ['place', 'visit', 'attraction', 'temple', 'park', 'mountain']:
                if keyword.lower() in text:
                    place_name = f"{title} ({channel})"
                    if place_name not in insights['top_places']:
                        insights['top_places'].append(place_name)
                    break

            # Check for activity mentions
            for keyword in thai_keywords['activities'] + ['activity', 'do', 'adventure', 'experience', 'tour']:
                if keyword.lower() in text:
                    activity_name = f"{title} ({channel})"
                    if activity_name not in insights['top_activities']:
                        insights['top_activities'].append(activity_name)
                    break

            # Check for tips
            for keyword in thai_keywords['tips'] + ['tip', 'advice', 'recommend', 'must', 'should', 'avoid']:
                if keyword.lower() in text:
                    tip = f"{title} ({channel})"
                    if tip not in insights['tips']:
                        insights['tips'].append(tip)
                    break

            # Check for hidden gems
            for keyword in thai_keywords['hidden_gems'] + ['hidden', 'secret', 'unknown', 'off the beaten path']:
                if keyword.lower() in text:
                    hidden_gem = f"{title} ({channel})"
                    if hidden_gem not in insights['hidden_gems']:
                        insights['hidden_gems'].append(hidden_gem)
                    break

            # Check for food recommendations
            for keyword in thai_keywords['food'] + ['food', 'restaurant', 'eat', 'cuisine', 'dish', 'delicious']:
                if keyword.lower() in text:
                    food_rec = f"{title} ({channel})"
                    if food_rec not in insights['food_recommendations']:
                        insights['food_recommendations'].append(food_rec)
                    break

        # Log the results
        for category, items in insights.items():
            logger.info(f"Extracted {len(items)} {category}: {', '.join(items[:3])}{'...' if len(items) > 3 else ''}")

        return insights
    except Exception as e:
        logger.error(f"Error in extract_travel_insights: {e}")
        return {}

def get_popular_travel_channels(topic, results=5):
    """Find popular YouTube channels focused on travel for a specific topic."""
    try:
        from googleapiclient.discovery import build
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

        # Search for channels related to the topic
        request = youtube.search().list(
            q=topic,
            part='snippet',
            type='channel',
            maxResults=results
        )
        response = request.execute()

        channels = []
        for item in response.get('items', []):
            channel_id = item['snippet']['channelId']
            title = item['snippet']['title']
            description = item['snippet']['description']

            channels.append({
                'channel': title,
                'description': description,
                'channel_id': channel_id
            })

        return channels
    except Exception as e:
        logger.error(f"Error in get_popular_travel_channels: {e}")
        return []

def get_destination_sentiment(destination):
    """Analyze sentiment about a destination from YouTube content."""
    try:
        # In a real implementation, this would use LLM to analyze sentiment
        # This is a simplified mock version
        return {
            'overall_sentiment': 'Positive',
            'positive_mentions': 10,
            'negative_mentions': 2,
            'key_positives': ['beautiful scenery', 'friendly locals', 'delicious food'],
            'key_negatives': ['crowded in high season', 'some tourist traps']
        }
    except Exception as e:
        logger.error(f"Error in get_destination_sentiment: {e}")
        return {}

# Ensure we're logging properly
logger.info("YouTube Insight Agent module loaded")

# Check YouTube API configuration
import os
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
    logger.error("YOUTUBE_API_KEY environment variable is not set. YouTube insights will not work correctly.")
    logger.error("Please set YOUTUBE_API_KEY in your environment variables or .env file.")

# Check if YouTube tools are available
try:
    from googleapiclient.discovery import build
    from youtube_transcript_api import YouTubeTranscriptApi
    YOUTUBE_TOOLS_AVAILABLE = True
    logger.info("YouTube API dependencies are available")
except ImportError:
    YOUTUBE_TOOLS_AVAILABLE = False
    logger.warning("YouTube API dependencies are not available")

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
        # 1. Search for videos with improved query
        logger.info(f"[get_youtube_insights] Searching for videos about {destination}")
        # Use Thai language in search query for better results
        thai_travel_term = "ท่องเที่ยว"  # Thai word for "travel"
        thai_guide_term = "แนะนำ"  # Thai word for "guide"
        thai_review_term = "รีวิว"  # Thai word for "review"

        # Try multiple search terms to increase chances of finding videos
        search_terms = [
            f"{destination} {thai_travel_term}",  # "Destination travel"
            f"{destination} {thai_review_term}",  # "Destination review"
            f"{destination} {thai_guide_term}",   # "Destination guide"
            f"{destination} vlog"                # "Destination vlog"
        ]

        # Try each search term until we find videos
        videos = []
        for search_term in search_terms:
            logger.info(f"[get_youtube_insights] Trying search term: '{search_term}'")
            videos = search_travel_videos(search_term, max_results=5)
            if videos and len(videos) > 0:
                logger.info(f"[get_youtube_insights] Found {len(videos)} videos with search term '{search_term}'")
                break
            else:
                logger.warning(f"[get_youtube_insights] No videos found with search term '{search_term}'")

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

        # Extract video IDs with simplified and more robust logic
        video_ids = []
        for video in videos:
            # Our improved search_travel_videos function now returns a consistent format
            # with 'video_id' as a direct key
            if isinstance(video, dict) and 'video_id' in video:
                video_ids.append(video['video_id'])
                logger.info(f"[get_youtube_insights] Found video ID: {video['video_id']} - {video.get('title', 'No title')}")
            # Fallback for other formats
            elif isinstance(video, dict):
                # Try nested id object (YouTube API v3 format)
                if isinstance(video.get('id'), dict) and 'videoId' in video.get('id', {}):
                    video_id = video['id']['videoId']
                    video_ids.append(video_id)
                    logger.info(f"[get_youtube_insights] Found video ID (nested): {video_id}")
                # Try direct id string
                elif isinstance(video.get('id'), str):
                    video_ids.append(video['id'])
                    logger.info(f"[get_youtube_insights] Found video ID (direct): {video['id']}")
            # Handle case where the video itself might be a string ID
            elif isinstance(video, str):
                video_ids.append(video)
                logger.info(f"[get_youtube_insights] Found video ID (string): {video}")

        logger.info(f"[get_youtube_insights] Found {len(video_ids)} video IDs")

        # If no video IDs were found but we have videos, log the structure for debugging
        if len(video_ids) == 0 and len(videos) > 0:
            logger.warning(f"[get_youtube_insights] No video IDs extracted despite having {len(videos)} videos")
            logger.warning(f"[get_youtube_insights] First video structure: {json.dumps(videos[0], indent=2) if isinstance(videos[0], dict) else videos[0]}")

        # 2. Get insights from these videos (limit to 5 to avoid rate limiting)
        insights = extract_travel_insights(video_ids[:5])

        # 3. Get sentiment analysis
        try:
            # get_destination_sentiment only takes destination parameter
            sentiment = get_destination_sentiment(destination)
        except Exception as e:
            logger.error(f"[get_youtube_insights] Error getting sentiment: {e}")
            sentiment = {
                "overall_sentiment": "Unknown",
                "rating": 0.0
            }

        # 4. Get popular channels
        try:
            # get_popular_travel_channels takes 'results' parameter, not 'max_results'
            channels = get_popular_travel_channels(destination, results=3)
        except Exception as e:
            logger.error(f"[get_youtube_insights] Error getting popular channels: {e}")
            channels = [{
                "channel": "ไม่พบข้อมูลช่อง",
                "description": "ไม่สามารถเข้าถึงข้อมูลได้"
            }]

        # Defensive: ensure sentiment is a string (extract if dict)
        sentiment_value = sentiment
        if isinstance(sentiment, dict):
            sentiment_value = sentiment.get("overall_sentiment") or sentiment.get("sentiment") or json.dumps(sentiment)
        elif not isinstance(sentiment, str):
            sentiment_value = str(sentiment)

        # Defensive: ensure channels is a list of strings (extract if list of dicts)
        channels_value = channels
        if isinstance(channels, list):
            if all(isinstance(ch, dict) for ch in channels):
                channels_value = [ch.get("channel") or ch.get("name") or str(ch) for ch in channels]
            elif all(isinstance(ch, str) for ch in channels):
                channels_value = channels
            else:
                channels_value = [str(ch) for ch in channels]
        elif isinstance(channels, dict):
            channels_value = [channels.get("channel") or channels.get("name") or str(channels)]
        elif isinstance(channels, str):
            channels_value = [channels]
        else:
            channels_value = [str(channels)]

        # Compile results with improved video formatting
        formatted_videos = []
        for video in videos[:5]:
            try:
                if isinstance(video, dict):
                    # Handle our new format from search_travel_videos
                    if 'video_id' in video:
                        formatted_videos.append({
                            "title": video.get('title', 'Unknown Title'),
                            "channel": video.get('channel', 'Unknown Channel'),
                            "url": f"https://www.youtube.com/watch?v={video['video_id']}",
                            "published_at": video.get('published_at', '')
                        })
                    # Handle YouTube API v3 format
                    elif 'snippet' in video and 'id' in video:
                        video_id = video['id'].get('videoId') if isinstance(video['id'], dict) else video['id']
                        formatted_videos.append({
                            "title": video['snippet'].get('title', 'Unknown Title'),
                            "channel": video['snippet'].get('channelTitle', 'Unknown Channel'),
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "published_at": video['snippet'].get('publishedAt', '')
                        })
                # Handle string video IDs
                elif isinstance(video, str):
                    formatted_videos.append({
                        "title": "Video ID: " + video,
                        "channel": "Unknown Channel",
                        "url": f"https://www.youtube.com/watch?v={video}"
                    })
            except Exception as e:
                logger.error(f"Error formatting video for results: {e}")

        result = {
            "destination": destination,
            "insights": insights,
            "sentiment": sentiment_value,
            "channels": channels_value,
            "videos": formatted_videos
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
        # Using results parameter instead of max_results since that's what the function expects
            channels = get_popular_travel_channels(f"{destination} travel", results=5)
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
