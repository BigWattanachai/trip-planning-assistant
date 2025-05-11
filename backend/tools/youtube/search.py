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
    youtube = init_youtube_api()
    if not youtube:
        logger.error("YouTube API not initialized")
        return []
    
    logger.info(f"Searching YouTube for: {query}")
    
    try:
        # Prepare the search query
        search_query = f"travel {query}"
        
        # Perform the search request
        search_response = youtube.search().list(
            q=search_query,
            part="id,snippet",
            maxResults=max_results,
            type="video",
            relevanceLanguage=language,
            regionCode=region_code,
            videoEmbeddable="true",
            videoCategoryId="19",  # Travel & Events category
        ).execute()
        
        # Process the search results
        videos = []
        for item in search_response.get("items", []):
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
                    
                    # Create the video information dictionary
                    video_info = {
                        "id": video_id,
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "publishedAt": item["snippet"]["publishedAt"],
                        "channelTitle": item["snippet"]["channelTitle"],
                        "thumbnailUrl": item["snippet"]["thumbnails"]["high"]["url"],
                        "viewCount": statistics.get("viewCount", "0"),
                        "likeCount": statistics.get("likeCount", "0"),
                        "duration": duration_readable,
                        "url": f"https://www.youtube.com/watch?v={video_id}"
                    }
                    videos.append(video_info)
        
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
            except:
                continue
        
        # If no preferred language found, get the first available
        if not transcript:
            transcript = transcript_list.find_transcript([])
        
        # Get the transcript data
        transcript_data = transcript.fetch()
        
        # Combine the text elements into a single string
        transcript_text = " ".join([item["text"] for item in transcript_data])
        
        # Clean up the transcript text
        transcript_text = clean_transcript(transcript_text)
        
        logger.info(f"Successfully retrieved transcript for video: {video_id}")
        return transcript_text
    
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
    # Search for videos
    videos = search_youtube_videos(query, max_results, language, region_code)
    
    # If get_transcripts is enabled, fetch transcripts for each video
    if get_transcripts and videos:
        for video in videos:
            transcript = get_video_transcript(video["id"], [language, "en"])
            video["transcript"] = transcript if transcript else ""
    
    return {
        "videos": videos,
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
    
    # Process each video to extract insights
    for video in videos:
        transcript = video.get("transcript", "")
        title = video.get("title", "")
        description = video.get("description", "")
        
        # Skip if no transcript available
        if not transcript:
            continue
        
        # Combine title, description and transcript for analysis
        content = f"{title}. {description}. {transcript}"
        
        # Extract popular places
        places = extract_popular_places(content)
        if places:
            insights["popular_places"].extend(places)
        
        # Extract local tips
        tips = extract_local_tips(content)
        if tips:
            insights["local_tips"].extend(tips)
        
        # Extract food recommendations
        food = extract_food_recommendations(content)
        if food:
            insights["food_recommendations"].extend(food)
        
        # Extract accommodation suggestions
        accommodations = extract_accommodation_suggestions(content)
        if accommodations:
            insights["accommodation_suggestions"].extend(accommodations)
        
        # Extract transportation advice
        transportation = extract_transportation_advice(content)
        if transportation:
            insights["transportation_advice"].extend(transportation)
        
        # Extract cultural insights
        culture = extract_cultural_insights(content)
        if culture:
            insights["cultural_insights"].extend(culture)
        
        # Extract activities
        activities = extract_activities(content)
        if activities:
            insights["activities"].extend(activities)
    
    # Deduplicate insights
    for category in insights:
        insights[category] = list(set(insights[category]))
    
    return {
        "insights": insights,
        "success": True,
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
    matches = re.findall(pattern, content, re.IGNORECASE)
    
    for match in matches:
        places.append(match.strip())
    
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
    matches = re.findall(pattern, content, re.IGNORECASE)
    
    for match in matches:
        # Clean up the tip and add if not too short
        tip = match.strip()
        if len(tip) > 10:  # Ensure the tip is substantive
            tips.append(tip)
    
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
    matches = re.findall(pattern, content, re.IGNORECASE)
    
    for match in matches:
        # Clean up and add if not too short
        recommendation = match.strip()
        if len(recommendation) > 8:
            recommendations.append(recommendation)
    
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
    matches = re.findall(pattern, content, re.IGNORECASE)
    
    for match in matches:
        # Clean up and add if not too short
        suggestion = match.strip()
        if len(suggestion) > 8:
            suggestions.append(suggestion)
    
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
    matches = re.findall(pattern, content, re.IGNORECASE)
    
    for match in matches:
        # Clean up and add if not too short
        transport_advice = match.strip()
        if len(transport_advice) > 8:
            advice.append(transport_advice)
    
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
    matches = re.findall(pattern, content, re.IGNORECASE)
    
    for match in matches:
        # Clean up and add if not too short
        insight = match.strip()
        if len(insight) > 10:
            insights.append(insight)
    
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
    matches = re.findall(pattern, content, re.IGNORECASE)
    
    for match in matches:
        # Clean up and add if not too short
        activity = match.strip()
        if len(activity) > 8:
            activities.append(activity)
    
    return activities
