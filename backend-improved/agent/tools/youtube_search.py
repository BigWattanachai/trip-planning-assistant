"""
YouTube search tools for the Travel Agent.
Provides functionality to search for travel-related videos and extract insights.
"""

import os
import logging
import json
import re
from typing import List, Dict, Any, Optional, Tuple
import googleapiclient.discovery
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

from config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Get the YouTube API key from settings
YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY
if not YOUTUBE_API_KEY:
    logger.warning("YOUTUBE_API_KEY not set. YouTube search functionality will not work.")

def init_youtube_api() -> Optional[Any]:
    """
    Initialize the YouTube API client.
    
    Returns:
        YouTube API client or None if initialization failed
    """
    if not YOUTUBE_API_KEY:
        logger.error("Cannot initialize YouTube API: No API key provided")
        return None

    try:
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=YOUTUBE_API_KEY
        )
        return youtube
    except Exception as e:
        logger.error(f"Failed to initialize YouTube API: {e}")
        return None

def search_youtube_videos(
    query: str,
    max_results: int = 5,
    language: str = "th",
    region_code: str = "TH"
) -> List[Dict[str, Any]]:
    """
    Search for YouTube videos related to the query.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        language: Preferred language for results
        region_code: Region code for localized results
        
    Returns:
        List of video information dictionaries
    """
    import datetime

    youtube = init_youtube_api()
    if not youtube:
        logger.error("YouTube API not initialized")
        return []

    logger.info(f"Searching YouTube for: {query}")

    try:
        # Prepare the search query - use Thai terms for better results
        if language == "th":
            search_query = f"{query} 2025"
        else:
            search_query = f"travel guide tips {query}"

        logger.info(f"Using search query: {search_query}")

        # Get current year for filtering recent videos
        current_year = datetime.datetime.now().year
        published_after = f"{current_year-1}-01-01T00:00:00Z"  # Videos from last year and current year

        # Perform the search request
        search_response = youtube.search().list(
            q=search_query,
            part="id,snippet",
            maxResults=max_results * 2,  # Request more videos to filter
            type="video",
            relevanceLanguage=language,
            regionCode=region_code,
            videoEmbeddable="true",
            videoCategoryId="19",  # Travel & Events category
            publishedAfter=published_after,  # Only recent videos
            videoCaption="closedCaption"  # Only videos with captions
        ).execute()

        # Extract video IDs
        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
        if not video_ids:
            logger.warning(f"No videos found for query: {query}")
            return []

        # Get detailed video information
        videos_response = youtube.videos().list(
            id=",".join(video_ids),
            part="snippet,contentDetails,statistics"
        ).execute()

        # Process video information
        videos = []
        for item in videos_response.get("items", []):
            video_id = item["id"]
            snippet = item["snippet"]
            statistics = item["statistics"]
            content_details = item["contentDetails"]

            # Parse duration
            duration = parse_youtube_duration(content_details.get("duration", "PT0S"))

            # Create video information dictionary
            video_info = {
                "id": video_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "channel": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
                "duration": duration,
                "views": int(statistics.get("viewCount", 0)),
                "likes": int(statistics.get("likeCount", 0)),
                "url": f"https://www.youtube.com/watch?v={video_id}"
            }

            videos.append(video_info)

        # Sort by views (most popular first) and limit to max_results
        videos.sort(key=lambda x: x["views"], reverse=True)
        return videos[:max_results]

    except HttpError as e:
        logger.error(f"YouTube API error: {e}")
        return []
    except Exception as e:
        logger.error(f"Error searching YouTube: {e}")
        return []

def get_video_transcript(
    video_id: str,
    languages: List[str] = ["th", "en"]
) -> Optional[str]:
    """
    Get the transcript of a YouTube video.
    
    Args:
        video_id: The YouTube video ID
        languages: List of preferred languages for the transcript
        
    Returns:
        The video transcript as a string, or None if not available
    """
    try:
        # Try to get the transcript in the preferred languages
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        except Exception as e:
            logger.warning(f"Could not list transcripts for video {video_id}: {e}")
            return None
        
        # First try to get manually created transcripts in preferred languages
        for lang in languages:
            try:
                transcript = transcript_list.find_manually_created_transcript([lang])
                transcript_data = transcript.fetch()
                return " ".join([entry["text"] for entry in transcript_data])
            except (NoTranscriptFound, TranscriptsDisabled, Exception):
                continue
        
        # Then try to get auto-generated transcripts in preferred languages
        for lang in languages:
            try:
                transcript = transcript_list.find_generated_transcript([lang])
                transcript_data = transcript.fetch()
                return " ".join([entry["text"] for entry in transcript_data])
            except (NoTranscriptFound, TranscriptsDisabled, Exception):
                continue
        
        # If no preferred language is found, try to get any transcript
        try:
            try:
                transcript = next(transcript_list._manually_created_transcripts.values().__iter__())
                transcript_data = transcript.fetch()
                return " ".join([entry["text"] for entry in transcript_data])
            except (StopIteration, NoTranscriptFound, TranscriptsDisabled, Exception):
                pass
                
            try:
                transcript = next(transcript_list._generated_transcripts.values().__iter__())
                transcript_data = transcript.fetch()
                return " ".join([entry["text"] for entry in transcript_data])
            except (StopIteration, NoTranscriptFound, TranscriptsDisabled, Exception):
                pass
        except Exception:
            pass
            
        return None
    
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        logger.warning(f"No transcript available for video {video_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error getting transcript for video {video_id}: {e}")
        return None

def search_youtube_with_transcripts(
    query: str,
    max_results: int = 3,
    language: str = "th",
    region_code: str = "TH",
    get_transcripts: bool = True
) -> Dict[str, Any]:
    """
    Search for YouTube videos and get their transcripts.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        language: Preferred language for results
        region_code: Region code for localized results
        get_transcripts: Whether to fetch video transcripts
        
    Returns:
        Dictionary with videos and transcripts
    """
    # Search for videos
    videos = search_youtube_videos(
        query=query,
        max_results=max_results,
        language=language,
        region_code=region_code
    )
    
    if not videos:
        logger.warning(f"No videos found for query: {query}")
        return {"videos": [], "query": query}
    
    # Get transcripts if requested
    if get_transcripts:
        transcript_success_count = 0
        for video in videos:
            try:
                video_id = video["id"]
                transcript = get_video_transcript(
                    video_id=video_id,
                    languages=[language, "en"]
                )
                
                if transcript:
                    # Clean and truncate transcript
                    video["transcript"] = clean_transcript(transcript)[:10000]  # Limit to 10k chars
                    transcript_success_count += 1
                else:
                    # Use video description as fallback if no transcript
                    video["transcript"] = video.get("description", "")
            except Exception as e:
                logger.warning(f"Error processing transcript for video {video.get('id')}: {e}")
                # Use video description as fallback
                video["transcript"] = video.get("description", "")
        
        logger.info(f"Successfully retrieved {transcript_success_count}/{len(videos)} transcripts for query: {query}")
    
    return {
        "videos": videos,
        "query": query
    }

def extract_travel_insights(videos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract travel insights from video information and transcripts.
    
    Args:
        videos: List of video information dictionaries with transcripts
        
    Returns:
        Dictionary with extracted insights
    """
    if not videos:
        return {"insights": {}, "success": False}
    
    # Combine all transcripts and descriptions
    all_content = ""
    for video in videos:
        if "transcript" in video and video["transcript"]:
            all_content += video["transcript"] + " "
        if "description" in video and video["description"]:
            all_content += video["description"] + " "
    
    if not all_content.strip():
        logger.warning("No content available to extract insights from")
        return {"insights": {}, "success": False}
    
    # Extract insights by category
    insights = {
        "popular_places": extract_popular_places(all_content),
        "local_tips": extract_local_tips(all_content),
        "food_recommendations": extract_food_recommendations(all_content),
        "accommodation_suggestions": extract_accommodation_suggestions(all_content),
        "transportation_advice": extract_transportation_advice(all_content),
        "cultural_insights": extract_cultural_insights(all_content),
        "activities": extract_activities(all_content)
    }
    
    # Check if we have any insights
    has_insights = any(len(items) > 0 for items in insights.values())
    
    return {
        "insights": insights,
        "success": has_insights
    }

def search_youtube_for_travel(
    query: str,
    destination: str = "",
    max_results: int = 3,
    language: str = "th"
) -> Dict[str, Any]:
    """
    Search YouTube for travel-related videos in direct API mode.
    
    Args:
        query: Search query
        destination: Destination name
        max_results: Maximum number of results
        language: Language code
        
    Returns:
        Dictionary with search results and insights
    """
    logger.info(f"YouTube search called with query: {query}, destination: {destination}")
    
    try:
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
        
        return result
    except Exception as e:
        logger.error(f"Error in YouTube search: {e}")
        return {
            "videos": [],
            "insights": {},
            "success": False,
            "error": str(e)
        }

def format_youtube_insights(insights: Dict[str, List[str]]) -> str:
    """
    Format YouTube insights for agent consumption.
    
    Args:
        insights: Dictionary of insights by category
        
    Returns:
        Formatted string with insights
    """
    if not insights:
        return ""
    
    formatted_insights = "\n\n### ข้อมูลจาก YouTube เกี่ยวกับจุดหมายปลายทาง ###\n"
    
    # Format popular places
    if "popular_places" in insights and insights["popular_places"]:
        formatted_insights += "\n🏠 สถานที่ยอดนิยม:\n"
        for place in insights["popular_places"][:5]:  # Limit to 5 items
            formatted_insights += f"- {place}\n"
    
    # Format activities
    if "activities" in insights and insights["activities"]:
        formatted_insights += "\n🏄‍♂️ กิจกรรมแนะนำ:\n"
        for activity in insights["activities"][:5]:  # Limit to 5 items
            formatted_insights += f"- {activity}\n"
    
    # Format food recommendations
    if "food_recommendations" in insights and insights["food_recommendations"]:
        formatted_insights += "\n🍜 อาหารที่ควรลอง:\n"
        for food in insights["food_recommendations"][:5]:  # Limit to 5 items
            formatted_insights += f"- {food}\n"
    
    # Format accommodation suggestions
    if "accommodation_suggestions" in insights and insights["accommodation_suggestions"]:
        formatted_insights += "\n🏨 ที่พักแนะนำ:\n"
        for accommodation in insights["accommodation_suggestions"][:5]:  # Limit to 5 items
            formatted_insights += f"- {accommodation}\n"
    
    # Format transportation advice
    if "transportation_advice" in insights and insights["transportation_advice"]:
        formatted_insights += "\n🚌 คำแนะนำด้านการเดินทาง:\n"
        for advice in insights["transportation_advice"][:5]:  # Limit to 5 items
            formatted_insights += f"- {advice}\n"
    
    # Format local tips
    if "local_tips" in insights and insights["local_tips"]:
        formatted_insights += "\n💡 เคล็ดลับจากคนท้องถิ่น:\n"
        for tip in insights["local_tips"][:5]:  # Limit to 5 items
            formatted_insights += f"- {tip}\n"
    
    # Format cultural insights
    if "cultural_insights" in insights and insights["cultural_insights"]:
        formatted_insights += "\n🏮 ข้อมูลทางวัฒนธรรม:\n"
        for insight in insights["cultural_insights"][:5]:  # Limit to 5 items
            formatted_insights += f"- {insight}\n"
    
    return formatted_insights

# Helper functions

def parse_youtube_duration(duration_str: str) -> str:
    """
    Parse YouTube duration format (ISO 8601) to a readable format.
    
    Args:
        duration_str: YouTube duration string (e.g., "PT1H30M15S")
        
    Returns:
        Readable duration string (e.g., "1:30:15")
    """
    # Extract hours, minutes, and seconds
    hours_match = re.search(r'(\d+)H', duration_str)
    minutes_match = re.search(r'(\d+)M', duration_str)
    seconds_match = re.search(r'(\d+)S', duration_str)
    
    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0
    seconds = int(seconds_match.group(1)) if seconds_match else 0
    
    # Format the duration
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def clean_transcript(text: str) -> str:
    """
    Clean the transcript text.
    
    Args:
        text: Raw transcript text
        
    Returns:
        Cleaned transcript text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove timestamps and other non-text elements
    text = re.sub(r'\[\d+:\d+\]', '', text)
    
    return text.strip()

def extract_popular_places(content: str) -> List[str]:
    """Extract popular places mentioned in the content."""
    places = []
    
    # Common patterns for popular places
    patterns = [
        r'(?:ต้องไป|ห้ามพลาด|แนะนำ|ที่เที่ยว|สถานที่ท่องเที่ยว|จุดชมวิว|แลนด์มาร์ค|landmark)(?:[^\n.]*?)((?:[^\n.]*?)[^\n.]*?)(?:เลย|นะ|ครับ|ค่ะ|เนอะ|ด้วย|จ้า|ที่สุด|มาก|\.|$)',
        r'(?:must-visit|popular|famous|best|top|scenic|beautiful)(?:[^\n.]*?)((?:[^\n.]*?)[^\n.]*?)(?:spot|place|location|attraction|site|destination|point|view|\.|$)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) > 0:
                place = match.group(1).strip()
                if place and len(place) > 3 and len(place) < 100:
                    places.append(place)
    
    # Remove duplicates and limit to 10 items
    return list(dict.fromkeys(places))[:10]

def extract_local_tips(content: str) -> List[str]:
    """Extract local tips mentioned in the content."""
    tips = []
    
    # Common patterns for local tips
    patterns = [
        r'(?:เคล็ดลับ|ข้อควรรู้|ควรระวัง|ต้องระวัง|อย่าลืม|ห้าม|ควร|แนะนำให้|ต้อง)(?:[^\n.]*?)((?:[^\n.]*?)[^\n.]*?)(?:นะ|ครับ|ค่ะ|เนอะ|ด้วย|จ้า|\.|$)',
        r'(?:tip|advice|recommend|suggestion|warning|caution|don\'t forget|remember to|make sure|be aware)(?:[^\n.]*?)((?:[^\n.]*?)[^\n.]*?)(?:when|while|during|if|\.|\!|$)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) > 0:
                tip = match.group(1).strip()
                if tip and len(tip) > 5 and len(tip) < 150:
                    tips.append(tip)
    
    # Remove duplicates and limit to 10 items
    return list(dict.fromkeys(tips))[:10]

def extract_food_recommendations(content: str) -> List[str]:
    """Extract food recommendations from the content."""
    foods = []
    
    # Common patterns for food recommendations
    patterns = [
        r'(?:อาหาร|ของกิน|ร้านอาหาร|เมนู|อาหารท้องถิ่น|อาหารขึ้นชื่อ|ต้องลอง|ห้ามพลาด)(?:[^\n.]*?)((?:[^\n.]*?)[^\n.]*?)(?:เลย|นะ|ครับ|ค่ะ|เนอะ|ด้วย|จ้า|ที่สุด|มาก|อร่อย|\.|$)',
        r'(?:food|dish|cuisine|restaurant|local food|specialty|must-try|delicious)(?:[^\n.]*?)((?:[^\n.]*?)[^\n.]*?)(?:is|are|when|while|during|if|\.|\!|$)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) > 0:
                food = match.group(1).strip()
                if food and len(food) > 3 and len(food) < 100:
                    foods.append(food)
    
    # Remove duplicates and limit to 10 items
    return list(dict.fromkeys(foods))[:10]

def extract_accommodation_suggestions(content: str) -> List[str]:
    """Extract accommodation suggestions from the content."""
    accommodations = []
    
    # Common patterns for accommodation suggestions
    patterns = [
        r'(?:ที่พัก|โรงแรม|รีสอร์ท|โฮสเทล|เกสต์เฮาส์|บูติครีสอร์ท|พูลวิลล่า)(?:[^\n.]*?)((?:[^\n.]*?)[^\n.]*?)(?:เลย|นะ|ครับ|ค่ะ|เนอะ|ด้วย|จ้า|ที่สุด|มาก|ดี|สวย|\.|$)',
        r'(?:accommodation|hotel|resort|hostel|guesthouse|stay|place to stay|boutique|villa)(?:[^\n.]*?)((?:[^\n.]*?)[^\n.]*?)(?:is|are|when|while|during|if|\.|\!|$)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) > 0:
                accommodation = match.group(1).strip()
                if accommodation and len(accommodation) > 3 and len(accommodation) < 100:
                    accommodations.append(accommodation)
    
    # Remove duplicates and limit to 10 items
    return list(dict.fromkeys(accommodations))[:10]

def extract_transportation_advice(content: str) -> List[str]:
    """Extract transportation advice from the content."""
    advice = []
    
    # Common patterns for transportation advice
    patterns = [
        r'(?:การเดินทาง|วิธีเดินทาง|รถ|เครื่องบิน|รถไฟ|รถทัวร์|รถโดยสาร|รถสาธารณะ|แท็กซี่|มอเตอร์ไซค์)(?:[^\n.]*?)((?:[^\n.]*?)[^\n.]*?)(?:เลย|นะ|ครับ|ค่ะ|เนอะ|ด้วย|จ้า|ที่สุด|มาก|\.|$)',
        r'(?:transport|transportation|travel|get around|bus|train|flight|taxi|motorbike|scooter|car|ferry|boat)(?:[^\n.]*?)((?:[^\n.]*?)[^\n.]*?)(?:is|are|when|while|during|if|\.|\!|$)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) > 0:
                transport = match.group(1).strip()
                if transport and len(transport) > 5 and len(transport) < 150:
                    advice.append(transport)
    
    # Remove duplicates and limit to 10 items
    return list(dict.fromkeys(advice))[:10]

def extract_cultural_insights(content: str) -> List[str]:
    """Extract cultural insights from the content."""
    insights = []
    
    # Common patterns for cultural insights
    patterns = [
        r'(?:วัฒนธรรม|ประเพณี|เทศกาล|พิธี|ความเชื่อ|ศาสนา|วิถีชีวิต)(?:[^\n.]*?)((?:[^\n.]*?)[^\n.]*?)(?:เลย|นะ|ครับ|ค่ะ|เนอะ|ด้วย|จ้า|ที่สุด|มาก|\.|$)',
        r'(?:culture|tradition|festival|ceremony|belief|religion|lifestyle|custom|ritual)(?:[^\n.]*?)((?:[^\n.]*?)[^\n.]*?)(?:is|are|when|while|during|if|\.|\!|$)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) > 0:
                insight = match.group(1).strip()
                if insight and len(insight) > 5 and len(insight) < 150:
                    insights.append(insight)
    
    # Remove duplicates and limit to 10 items
    return list(dict.fromkeys(insights))[:10]

def extract_activities(content: str) -> List[str]:
    """Extract activities from the content."""
    activities = []
    
    # Common patterns for activities
    patterns = [
        r'(?:กิจกรรม|ทำอะไร|เล่น|ลอง|ทดลอง|ผจญภัย|สนุก|น่าตื่นเต้น)(?:[^\n.]*?)((?:[^\n.]*?)[^\n.]*?)(?:เลย|นะ|ครับ|ค่ะ|เนอะ|ด้วย|จ้า|ที่สุด|มาก|\.|$)',
        r'(?:activity|thing to do|adventure|experience|try|fun|exciting|enjoy)(?:[^\n.]*?)((?:[^\n.]*?)[^\n.]*?)(?:is|are|when|while|during|if|\.|\!|$)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) > 0:
                activity = match.group(1).strip()
                if activity and len(activity) > 3 and len(activity) < 100:
                    activities.append(activity)
    
    # Remove duplicates and limit to 10 items
    return list(dict.fromkeys(activities))[:10]
