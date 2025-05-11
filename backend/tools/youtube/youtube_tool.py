"""
YouTube search tools for the Travel Agent

This module provides tools to integrate YouTube search functionality with the Agent Development Kit (ADK).
"""

import logging
from typing import Dict, Any, List, Optional
import os
import sys
import pathlib

# Add the parent directory to sys.path to allow imports
parent_dir = str(pathlib.Path(__file__).parent.parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the YouTube search functions
try:
    from tools.youtube.search import (
        search_youtube_with_transcripts,
        extract_travel_insights
    )
except ImportError:
    try:
        from backend.tools.youtube.search import (
            search_youtube_with_transcripts,
            extract_travel_insights
        )
    except ImportError:
        logger.error("Failed to import YouTube search functions")

        # Define placeholders in case imports fail
        def search_youtube_with_transcripts(query, max_results=3, language="th", region_code="TH", get_transcripts=True):
            logger.error("YouTube search not available: Function not properly imported")
            return {"videos": [], "query": query}

        def extract_travel_insights(videos):
            logger.error("Travel insights extraction not available: Function not properly imported")
            return {"insights": {}, "success": False}

# Check if Vertex AI/ADK mode is enabled
USE_VERTEX_AI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes")

# Define YouTube search tool for ADK
if USE_VERTEX_AI:
    try:
        from google.adk.tools import ToolContext

        def youtube_search_tool(
            query: str,
            destination: str = "",
            max_results: int = 3,
            language: str = "th",
            tool_context: ToolContext = None
        ) -> Dict[str, Any]:
            """
            Search YouTube for travel-related videos about a destination.

            Args:
                query: Search query
                destination: Destination name
                max_results: Maximum number of results
                language: Language code
                tool_context: ADK Tool Context

            Returns:
                Dictionary with search results and insights
            """
            logger.info(f"YouTube search tool called with query: {query}, destination: {destination}")

            # Build the search query
            search_query = query
            if destination and destination not in query:
                search_query = f"{destination} {query}"

            # Determine the region code based on language
            region_code = "TH" if language == "th" else "US"

            # Search for videos with transcripts
            search_results = search_youtube_with_transcripts(
                search_query,
                max_results=max_results,
                language=language,
                region_code=region_code,
                get_transcripts=True
            )

            # Extract travel insights
            insights = extract_travel_insights(search_results.get("videos", []))

            # Combine results
            result = {
                "videos": search_results.get("videos", []),
                "insights": insights.get("insights", {}),
                "success": insights.get("success", False)
            }

            # Store in the tool context if available
            if tool_context and result["videos"]:
                tool_context.state["youtube_videos"] = result["videos"]
                tool_context.state["youtube_insights"] = result["insights"]
                logger.info(f"Stored YouTube results in tool context")

            logger.info(f"YouTube search tool found {len(result['videos'])} videos")
            return result

        youtube_search_tool.description = """
        Search YouTube for travel-related videos about a destination.
        Returns information about videos and extracts travel insights from transcripts.
        """
    except ImportError as e:
        logger.error(f"Failed to import ADK components: {e}")
        youtube_search_tool = None

# Function for Direct API mode
def search_youtube_for_travel(
    query: str,
    destination: str = "",
    max_results: int = 3,
    language: str = "th"
) -> Dict[str, Any]:
    """
    Search YouTube for travel-related videos in direct API mode

    Args:
        query: Search query
        destination: Destination name
        max_results: Maximum number of results
        language: Language code

    Returns:
        Dictionary with search results and insights
    """
    logger.info(f"YouTube search in direct API mode: {query}, destination: {destination}")

    try:
        # Build the search query
        search_query = query
        if destination and destination not in query:
            search_query = f"{destination} {query}"

        logger.info(f"Final YouTube search query: {search_query}")

        # Determine the region code based on language
        region_code = "TH" if language == "th" else "US"

        # Search for videos with transcripts
        search_results = search_youtube_with_transcripts(
            search_query,
            max_results=max_results,
            language=language,
            region_code=region_code,
            get_transcripts=True
        )

        # Log search results
        video_count = len(search_results.get("videos", []))
        logger.info(f"Found {video_count} videos with transcripts for {destination}")

        # Extract travel insights
        insights = extract_travel_insights(search_results.get("videos", []))

        # Log insights
        insight_categories = insights.get("insights", {})
        total_insights = sum(len(insight_categories.get(cat, [])) for cat in insight_categories)
        logger.info(f"Extracted {total_insights} total insights across {len(insight_categories)} categories")

        # Return combined results
        result = {
            "videos": search_results.get("videos", []),
            "insights": insights.get("insights", {}),
            "success": insights.get("success", False)
        }

        return result
    except Exception as e:
        logger.error(f"Error in search_youtube_for_travel: {e}")
        return {
            "videos": [],
            "insights": {},
            "success": False,
            "error": str(e)
        }

def format_youtube_insights_for_agent(insights: Dict[str, List[str]]) -> str:
    """
    Format YouTube insights for agent consumption

    Args:
        insights: Dictionary of insights by category

    Returns:
        Formatted string with insights
    """
    if not insights:
        return "ไม่พบข้อมูลจากวิดีโอ YouTube"

    formatted = "ข้อมูลจากวิดีโอ YouTube:\n\n"

    # Add popular places
    if insights.get("popular_places"):
        formatted += "🏙️ สถานที่ยอดนิยม:\n"
        for place in insights["popular_places"][:5]:
            # Ensure the place is a string
            if isinstance(place, tuple):
                place_str = place[0] if place and len(place) > 0 else "ไม่ระบุ"
            else:
                place_str = str(place)
            formatted += f"- {place_str}\n"
        formatted += "\n"

    # Add local tips
    if insights.get("local_tips"):
        formatted += "💡 คำแนะนำจากคนท้องถิ่น:\n"
        for tip in insights["local_tips"][:5]:
            # Ensure the tip is a string
            if isinstance(tip, tuple):
                tip_str = tip[0] if tip and len(tip) > 0 else "ไม่ระบุ"
            else:
                tip_str = str(tip)
            formatted += f"- {tip_str}\n"
        formatted += "\n"

    # Add food recommendations
    if insights.get("food_recommendations"):
        formatted += "🍲 อาหารแนะนำ:\n"
        for food in insights["food_recommendations"][:5]:
            # Ensure the food is a string
            if isinstance(food, tuple):
                food_str = food[0] if food and len(food) > 0 else "ไม่ระบุ"
            else:
                food_str = str(food)
            formatted += f"- {food_str}\n"
        formatted += "\n"

    # Add accommodation suggestions
    if insights.get("accommodation_suggestions"):
        formatted += "🏨 ที่พักแนะนำ:\n"
        for accommodation in insights["accommodation_suggestions"][:5]:
            # Ensure the accommodation is a string
            if isinstance(accommodation, tuple):
                accommodation_str = accommodation[0] if accommodation and len(accommodation) > 0 else "ไม่ระบุ"
            else:
                accommodation_str = str(accommodation)
            formatted += f"- {accommodation_str}\n"
        formatted += "\n"

    # Add transportation advice
    if insights.get("transportation_advice"):
        formatted += "🚌 คำแนะนำเกี่ยวกับการเดินทาง:\n"
        for advice in insights["transportation_advice"][:5]:
            # Ensure the advice is a string
            if isinstance(advice, tuple):
                advice_str = advice[0] if advice and len(advice) > 0 else "ไม่ระบุ"
            else:
                advice_str = str(advice)
            formatted += f"- {advice_str}\n"
        formatted += "\n"

    # Add cultural insights
    if insights.get("cultural_insights"):
        formatted += "🏮 ข้อมูลทางวัฒนธรรม:\n"
        for culture in insights["cultural_insights"][:5]:
            # Ensure the culture is a string
            if isinstance(culture, tuple):
                culture_str = culture[0] if culture and len(culture) > 0 else "ไม่ระบุ"
            else:
                culture_str = str(culture)
            formatted += f"- {culture_str}\n"
        formatted += "\n"

    # Add activities
    if insights.get("activities"):
        formatted += "🏄‍♂️ กิจกรรมแนะนำ:\n"
        for activity in insights["activities"][:5]:
            # Ensure the activity is a string
            if isinstance(activity, tuple):
                activity_str = activity[0] if activity and len(activity) > 0 else "ไม่ระบุ"
            else:
                activity_str = str(activity)
            formatted += f"- {activity_str}\n"
        formatted += "\n"

    return formatted

def format_youtube_videos_for_agent(videos: List[Dict[str, Any]]) -> str:
    """
    Format YouTube video information for agent consumption

    Args:
        videos: List of video information dictionaries

    Returns:
        Formatted string with video information
    """
    if not videos:
        return "ไม่พบวิดีโอที่เกี่ยวข้อง"

    formatted = "วิดีโอที่เกี่ยวข้อง:\n\n"

    for i, video in enumerate(videos[:3], 1):
        formatted += f"{i}. {video.get('title')}\n"
        formatted += f"   ช่อง: {video.get('channelTitle')}\n"
        formatted += f"   ความยาว: {video.get('duration')}\n"
        formatted += f"   ยอดวิว: {video.get('viewCount')}\n"
        formatted += f"   URL: {video.get('url')}\n\n"

    return formatted
