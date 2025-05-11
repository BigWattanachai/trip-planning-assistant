"""
YouTube search functionality for the Travel Agent

This module provides functions to search for YouTube videos related to
travel destinations and extract valuable information from them.
"""

import os
import logging
import json
import re
from typing import List, Dict, Any, Optional, Tuple
import googleapiclient.discovery
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get the YouTube API key from environment variables
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
if not YOUTUBE_API_KEY:
    logger.warning("YOUTUBE_API_KEY not set. YouTube search functionality will not work.")

def init_youtube_api() -> Optional[Any]:
    """
    Initialize the YouTube API client

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
    Search for YouTube videos related to the query

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
            search_query = f"{query} ท่องเที่ยว คู่มือ เคล็ดลับ"
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

        # Process the search results
        videos = []
        for item in search_response.get("items", []):
            # Stop if we have enough videos
            if len(videos) >= max_results:
                break

            try:
                if item["id"]["kind"] == "youtube#video":
                    video_id = item["id"]["videoId"]

                    # Get video statistics and details
                    video_response = youtube.videos().list(
                        part="statistics,contentDetails",
                        id=video_id
                    ).execute()

                    if video_response["items"]:
                        statistics = video_response["items"][0].get("statistics", {})
                        content_details = video_response["items"][0].get("contentDetails", {})

                        # Extract duration in a readable format
                        duration = content_details.get("duration", "PT0M0S")
                        duration_readable = parse_youtube_duration(duration)

                        # Get published date and check if it's recent
                        published_at = item["snippet"]["publishedAt"]

                        # Create the video information dictionary
                        video_info = {
                            "id": video_id,
                            "title": item["snippet"]["title"],
                            "description": item["snippet"]["description"],
                            "publishedAt": published_at,
                            "channelTitle": item["snippet"]["channelTitle"],
                            "thumbnailUrl": item["snippet"]["thumbnails"]["high"]["url"],
                            "viewCount": statistics.get("viewCount", "0"),
                            "likeCount": statistics.get("likeCount", "0"),
                            "duration": duration_readable,
                            "url": f"https://www.youtube.com/watch?v={video_id}"
                        }
                        videos.append(video_info)
                        logger.info(f"Added video: {video_info['title']} (ID: {video_id}, Published: {published_at})")
            except Exception as e:
                logger.error(f"Error processing video item: {e}")

        logger.info(f"Found {len(videos)} YouTube videos for query: {query}")
        return videos

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
    Get the transcript of a YouTube video

    Args:
        video_id: The YouTube video ID
        languages: List of preferred languages for the transcript

    Returns:
        The video transcript as a string, or None if not available
    """
    try:
        logger.info(f"Getting transcript for video: {video_id}")

        # Try to get the transcript in the preferred languages
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try each language in order of preference
        transcript = None
        for lang in languages:
            try:
                transcript = transcript_list.find_transcript([lang])
                break
            except Exception as e:
                logger.debug(f"Could not find transcript in {lang}: {e}")
                continue

        # If no preferred language found, get the first available
        if not transcript:
            try:
                transcript = transcript_list.find_transcript([])
            except Exception as e:
                logger.warning(f"Could not find any transcript: {e}")
                return None

        # Get the transcript data
        try:
            transcript_data = transcript.fetch()

            # Combine the text elements into a single string
            transcript_text = " ".join([item["text"] for item in transcript_data])

            # Clean up the transcript text
            transcript_text = clean_transcript(transcript_text)

            logger.info(f"Successfully retrieved transcript for video: {video_id}")
            return transcript_text
        except Exception as e:
            logger.error(f"Error fetching transcript data: {e}")
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
    Search for YouTube videos and get their transcripts

    Args:
        query: The search query
        max_results: Maximum number of results to return
        language: Preferred language for results
        region_code: Region code for localized results
        get_transcripts: Whether to fetch video transcripts

    Returns:
        Dictionary with videos and transcripts
    """
    # Search for videos - request more videos than needed in case some don't have transcripts
    search_max = max_results * 2 if get_transcripts else max_results
    videos = search_youtube_videos(query, search_max, language, region_code)

    # If get_transcripts is enabled, fetch transcripts for each video
    videos_with_transcripts = []
    if get_transcripts and videos:
        for video in videos:
            try:
                transcript = get_video_transcript(video["id"], [language, "en"])
                if transcript:  # Only include videos with transcripts
                    video["transcript"] = transcript
                    videos_with_transcripts.append(video)
                    # Break if we have enough videos with transcripts
                    if len(videos_with_transcripts) >= max_results:
                        break
                else:
                    logger.warning(f"No transcript available for video {video['id']} - skipping")
            except Exception as e:
                logger.error(f"Error getting transcript for video {video['id']}: {e}")
    else:
        videos_with_transcripts = videos[:max_results]

    logger.info(f"Found {len(videos_with_transcripts)} videos with transcripts out of {len(videos)} total videos")

    return {
        "videos": videos_with_transcripts,
        "query": query
    }

def extract_travel_insights(
    videos: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Extract travel insights from video information and transcripts

    Args:
        videos: List of video information dictionaries with transcripts

    Returns:
        Dictionary with extracted insights
    """
    if not videos:
        return {"insights": {}, "success": False}

    # Initialize insights dictionary
    insights = {
        "popular_places": [],
        "local_tips": [],
        "food_recommendations": [],
        "accommodation_suggestions": [],
        "transportation_advice": [],
        "cultural_insights": [],
        "activities": []
    }

    try:
        # Process each video to extract insights
        for video in videos:
            try:
                transcript = video.get("transcript", "")
                title = video.get("title", "")
                description = video.get("description", "")

                # Skip if no transcript available
                if not transcript:
                    logger.warning(f"No transcript available for video {video.get('id', 'unknown')}")
                    continue

                # Combine title, description and transcript for analysis
                content = f"{title}. {description}. {transcript}"

                # Extract popular places
                try:
                    places = extract_popular_places(content)
                    if places:
                        insights["popular_places"].extend(places)
                except Exception as e:
                    logger.error(f"Error extracting popular places: {e}")

                # Extract local tips
                try:
                    tips = extract_local_tips(content)
                    if tips:
                        insights["local_tips"].extend(tips)
                except Exception as e:
                    logger.error(f"Error extracting local tips: {e}")

                # Extract food recommendations
                try:
                    food = extract_food_recommendations(content)
                    if food:
                        insights["food_recommendations"].extend(food)
                except Exception as e:
                    logger.error(f"Error extracting food recommendations: {e}")

                # Extract accommodation suggestions
                try:
                    accommodations = extract_accommodation_suggestions(content)
                    if accommodations:
                        insights["accommodation_suggestions"].extend(accommodations)
                except Exception as e:
                    logger.error(f"Error extracting accommodation suggestions: {e}")

                # Extract transportation advice
                try:
                    transportation = extract_transportation_advice(content)
                    if transportation:
                        insights["transportation_advice"].extend(transportation)
                except Exception as e:
                    logger.error(f"Error extracting transportation advice: {e}")

                # Extract cultural insights
                try:
                    culture = extract_cultural_insights(content)
                    if culture:
                        insights["cultural_insights"].extend(culture)
                except Exception as e:
                    logger.error(f"Error extracting cultural insights: {e}")

                # Extract activities
                try:
                    activities = extract_activities(content)
                    if activities:
                        insights["activities"].extend(activities)
                except Exception as e:
                    logger.error(f"Error extracting activities: {e}")

            except Exception as e:
                logger.error(f"Error processing video {video.get('id', 'unknown')}: {e}")
                continue

        # Deduplicate insights
        for category in insights:
            try:
                insights[category] = list(set(insights[category]))
            except Exception as e:
                logger.error(f"Error deduplicating {category}: {e}")
                insights[category] = insights[category][:10] if len(insights[category]) > 10 else insights[category]

        return {
            "insights": insights,
            "success": True,
            "video_count": len(videos)
        }
    except Exception as e:
        logger.error(f"Error extracting travel insights: {e}")
        return {
            "insights": insights,
            "success": False,
            "error": str(e),
            "video_count": len(videos)
        }

# Helper functions

def parse_youtube_duration(duration_str: str) -> str:
    """
    Parse YouTube duration format (ISO 8601) to a readable format

    Args:
        duration_str: YouTube duration string (e.g., "PT1H30M15S")

    Returns:
        Readable duration string (e.g., "1:30:15")
    """
    regex = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
    match = re.match(regex, duration_str)

    if not match:
        return "0:00"

    hours, minutes, seconds = match.groups()
    hours = int(hours) if hours else 0
    minutes = int(minutes) if minutes else 0
    seconds = int(seconds) if seconds else 0

    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def clean_transcript(text: str) -> str:
    """
    Clean the transcript text

    Args:
        text: Raw transcript text

    Returns:
        Cleaned transcript text
    """
    # Remove special characters and extra spaces
    text = re.sub(r'\[.*?\]', '', text)  # Remove text in square brackets
    text = re.sub(r'\s+', ' ', text)     # Replace multiple spaces with a single space
    return text.strip()

def extract_popular_places(content: str) -> List[str]:
    """Extract popular places mentioned in the content"""
    places = []

    # Keywords for popular places
    keywords = [
        r"must(-|\s)visit", r"popular", r"famous", r"attraction", r"landmark",
        r"ต้องไป", r"ที่นิยม", r"ที่มีชื่อเสียง", r"แลนด์มาร์ค", r"สถานที่ท่องเที่ยว",
    ]

    # Create regex pattern
    pattern = r"(?:" + "|".join(keywords) + r").*?(?:is|are|คือ)\s+([^.,!?]+)"

    try:
        matches = re.findall(pattern, content, re.IGNORECASE)

        for match in matches:
            if match and isinstance(match, str):
                places.append(match.strip())
            elif isinstance(match, tuple) and match:
                # If it's a tuple, take the first element
                places.append(str(match[0]).strip())
    except Exception as e:
        logging.error(f"Error extracting popular places: {e}")

    return places

def extract_local_tips(content: str) -> List[str]:
    """Extract local tips mentioned in the content"""
    tips = []

    # Keywords for local tips
    keywords = [
        r"tip", r"advice", r"recommend", r"suggestion", r"local",
        r"คำแนะนำ", r"ข้อแนะนำ", r"แนะนำ", r"ท้องถิ่น"
    ]

    # Create regex pattern
    pattern = r"(?:" + "|".join(keywords) + r")\s+([^.,!?;]+)"

    try:
        matches = re.findall(pattern, content, re.IGNORECASE)

        for match in matches:
            # Handle both string and tuple matches
            if isinstance(match, str):
                tip = match.strip()
                if len(tip) > 10:  # Ensure the tip is substantive
                    tips.append(tip)
            elif isinstance(match, tuple) and match:
                # If it's a tuple, take the first element
                tip = str(match[0]).strip()
                if len(tip) > 10:  # Ensure the tip is substantive
                    tips.append(tip)
    except Exception as e:
        logging.error(f"Error extracting local tips: {e}")

    return tips

def extract_food_recommendations(content: str) -> List[str]:
    """Extract food recommendations from the content"""
    recommendations = []

    # Keywords for food recommendations
    keywords = [
        r"food", r"dish", r"cuisine", r"eat", r"restaurant", r"meal", r"menu",
        r"อาหาร", r"จาน", r"ร้านอาหาร", r"ทาน", r"กิน", r"เมนู"
    ]

    # Create regex pattern
    pattern = r"(?:" + "|".join(keywords) + r")\s+([^.,!?;]+)"

    try:
        matches = re.findall(pattern, content, re.IGNORECASE)

        for match in matches:
            # Handle both string and tuple matches
            if isinstance(match, str):
                recommendation = match.strip()
                if len(recommendation) > 8:
                    recommendations.append(recommendation)
            elif isinstance(match, tuple) and match:
                # If it's a tuple, take the first element
                recommendation = str(match[0]).strip()
                if len(recommendation) > 8:
                    recommendations.append(recommendation)
    except Exception as e:
        logging.error(f"Error extracting food recommendations: {e}")

    return recommendations

def extract_accommodation_suggestions(content: str) -> List[str]:
    """Extract accommodation suggestions from the content"""
    suggestions = []

    # Keywords for accommodation suggestions
    keywords = [
        r"hotel", r"stay", r"hostel", r"resort", r"accommodation", r"room",
        r"โรงแรม", r"ที่พัก", r"โฮสเทล", r"รีสอร์ท", r"ห้องพัก"
    ]

    # Create regex pattern
    pattern = r"(?:" + "|".join(keywords) + r")\s+([^.,!?;]+)"

    try:
        matches = re.findall(pattern, content, re.IGNORECASE)

        for match in matches:
            # Handle both string and tuple matches
            if isinstance(match, str):
                suggestion = match.strip()
                if len(suggestion) > 8:
                    suggestions.append(suggestion)
            elif isinstance(match, tuple) and match:
                # If it's a tuple, take the first element
                suggestion = str(match[0]).strip()
                if len(suggestion) > 8:
                    suggestions.append(suggestion)
    except Exception as e:
        logging.error(f"Error extracting accommodation suggestions: {e}")

    return suggestions

def extract_transportation_advice(content: str) -> List[str]:
    """Extract transportation advice from the content"""
    advice = []

    # Keywords for transportation advice
    keywords = [
        r"transport", r"travel", r"get around", r"bus", r"train", r"taxi", r"car", r"flight",
        r"การเดินทาง", r"รถ", r"รถไฟ", r"แท็กซี่", r"เครื่องบิน", r"เดินทาง"
    ]

    # Create regex pattern
    pattern = r"(?:" + "|".join(keywords) + r")\s+([^.,!?;]+)"

    try:
        matches = re.findall(pattern, content, re.IGNORECASE)

        for match in matches:
            # Handle both string and tuple matches
            if isinstance(match, str):
                transport_advice = match.strip()
                if len(transport_advice) > 8:
                    advice.append(transport_advice)
            elif isinstance(match, tuple) and match:
                # If it's a tuple, take the first element
                transport_advice = str(match[0]).strip()
                if len(transport_advice) > 8:
                    advice.append(transport_advice)
    except Exception as e:
        logging.error(f"Error extracting transportation advice: {e}")

    return advice

def extract_cultural_insights(content: str) -> List[str]:
    """Extract cultural insights from the content"""
    insights = []

    # Keywords for cultural insights
    keywords = [
        r"culture", r"tradition", r"custom", r"people", r"local", r"etiquette",
        r"วัฒนธรรม", r"ประเพณี", r"ความเชื่อ", r"ท้องถิ่น", r"มารยาท"
    ]

    # Create regex pattern
    pattern = r"(?:" + "|".join(keywords) + r")\s+([^.,!?;]+)"

    try:
        matches = re.findall(pattern, content, re.IGNORECASE)

        for match in matches:
            # Handle both string and tuple matches
            if isinstance(match, str):
                insight = match.strip()
                if len(insight) > 10:
                    insights.append(insight)
            elif isinstance(match, tuple) and match:
                # If it's a tuple, take the first element
                insight = str(match[0]).strip()
                if len(insight) > 10:
                    insights.append(insight)
    except Exception as e:
        logging.error(f"Error extracting cultural insights: {e}")

    return insights

def extract_activities(content: str) -> List[str]:
    """Extract activities from the content"""
    activities = []

    # Keywords for activities
    keywords = [
        r"activity", r"do", r"experience", r"adventure", r"tour", r"visit",
        r"กิจกรรม", r"ทำ", r"ประสบการณ์", r"ทัวร์", r"เยี่ยมชม"
    ]

    # Create regex pattern
    pattern = r"(?:" + "|".join(keywords) + r")\s+([^.,!?;]+)"

    try:
        matches = re.findall(pattern, content, re.IGNORECASE)

        for match in matches:
            # Handle both string and tuple matches
            if isinstance(match, str):
                activity = match.strip()
                if len(activity) > 8:
                    activities.append(activity)
            elif isinstance(match, tuple) and match:
                # If it's a tuple, take the first element
                activity = str(match[0]).strip()
                if len(activity) > 8:
                    activities.append(activity)
    except Exception as e:
        logging.error(f"Error extracting activities: {e}")

    return activities
