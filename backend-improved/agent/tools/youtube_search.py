"""
YouTube search tool for retrieving video insights about travel destinations.
"""
import os
import logging
import json
import re
from typing import Dict, List, Any, Optional, Union

from config import settings

logger = logging.getLogger(__name__)

def search_youtube_for_travel(
    query: str = "",
    destination: str = "", 
    max_results: int = 3,
    language: str = "th"
) -> Dict[str, Any]:
    """
    Searches YouTube for travel-related videos about a destination.
    
    Args:
        query: The search query 
        destination: The destination to search for
        max_results: The maximum number of results to return
        language: The preferred language for results
        
    Returns:
        Dictionary containing search results, video information, and extracted insights
    """
    # Check if YouTube API key is set
    youtube_api_key = settings.YOUTUBE_API_KEY
    if not youtube_api_key:
        logger.warning("YOUTUBE_API_KEY not set. YouTube search capabilities will be limited.")
        return {"success": False, "error": "YouTube API key not available", "videos": []}
    
    try:
        # Import necessary libraries
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        
        # Combine query and destination if both provided
        search_query = query
        if destination and destination not in search_query:
            if search_query:
                search_query = f"{search_query} {destination}"
            else:
                search_query = destination
        
        logger.info(f"Searching YouTube for: {search_query}")
        
        # Initialize YouTube API client
        youtube = build("youtube", "v3", developerKey=youtube_api_key)
        
        # Filter for language if specified
        relevance_language = language if language else None
        
        # Search for videos
        search_response = youtube.search().list(
            q=search_query,
            part="id,snippet",
            maxResults=max_results,
            type="video",
            relevanceLanguage=relevance_language,
            videoDuration="medium"  # Medium length videos (4-20 mins)
        ).execute()
        
        # Extract video IDs
        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
        
        if not video_ids:
            logger.warning(f"No YouTube videos found for: {search_query}")
            return {"success": False, "error": "No videos found", "videos": []}
        
        # Get video details
        video_response = youtube.videos().list(
            id=",".join(video_ids),
            part="snippet,contentDetails,statistics"
        ).execute()
        
        # Process video information
        videos = []
        for item in video_response.get("items", []):
            video_info = {
                "id": item["id"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "published_at": item["snippet"]["publishedAt"],
                "channel": item["snippet"]["channelTitle"],
                "view_count": item["statistics"].get("viewCount", "0"),
                "like_count": item["statistics"].get("likeCount", "0"),
                "comment_count": item["statistics"].get("commentCount", "0"),
                "url": f"https://www.youtube.com/watch?v={item['id']}"
            }
            videos.append(video_info)
        
        # Extract insights from video information
        insights = extract_youtube_insights(videos, destination)
        
        # Return results
        return {
            "success": True,
            "videos": videos, 
            "insights": insights
        }
    
    except ImportError as e:
        logger.error(f"Failed to import required libraries for YouTube search: {e}")
        return {"success": False, "error": f"Import error: {e}", "videos": []}
    except Exception as e:
        logger.error(f"Error searching YouTube: {e}")
        return {"success": False, "error": str(e), "videos": []}

def extract_youtube_insights(videos: List[Dict[str, Any]], destination: str = "") -> Dict[str, Any]:
    """
    Extracts travel insights from YouTube video information.
    
    Args:
        videos: List of video information dictionaries
        destination: The destination to extract insights for
        
    Returns:
        Dictionary containing extracted insights
    """
    if not videos:
        return {}
    
    # Initialize insights
    insights = {
        "top_attractions": [],
        "local_tips": [],
        "recommended_activities": [],
        "food_recommendations": [],
        "accommodation_tips": [],
        "transportation_info": [],
        "destination": destination
    }
    
    # Keywords to match for different categories
    attraction_keywords = [
        "สถานที่ท่องเที่ยว", "จุดเที่ยว", "ไฮไลท์", "highlights", "attractions", 
        "landmark", "must visit", "must see", "ห้ามพลาด", "ที่เที่ยว"
    ]
    
    activity_keywords = [
        "กิจกรรม", "activities", "ทำอะไร", "things to do", "experience", 
        "adventure", "เล่น", "สนุก", "ประสบการณ์"
    ]
    
    food_keywords = [
        "อาหาร", "ร้านอาหาร", "food", "cuisine", "ของกิน", "อร่อย", "ร้านดัง",
        "restaurant", "cafe", "ร้านเด็ด", "เมนู", "กิน"
    ]
    
    accommodation_keywords = [
        "ที่พัก", "โรงแรม", "รีสอร์ท", "hotel", "resort", "hostel", "พัก", 
        "ห้องพัก", "นอน", "homestay", "โฮมสเตย์"
    ]
    
    transportation_keywords = [
        "เดินทาง", "transportation", "รถ", "เครื่องบิน", "รถไฟ", "car", "train",
        "วิธีไป", "how to get", "เดินทางไป", "ขนส่ง", "เดิน", "local transport"
    ]
    
    # Extract insights from video titles and descriptions
    for video in videos:
        title = video.get("title", "").lower()
        description = video.get("description", "").lower()
        combined_text = title + " " + description
        
        # Extract attractions
        for keyword in attraction_keywords:
            if keyword.lower() in combined_text:
                # Look for attraction names in the text
                attraction_pattern = rf'(?:ที่เที่ยว|สถานที่|ไฮไลท์|จุด|แลนด์มาร์ค|attractions?|places?|visit|see)\s?[:-]?\s?([^\n.,]+)'
                matches = re.findall(attraction_pattern, combined_text, re.IGNORECASE)
                for match in matches:
                    if len(match) > 3 and len(match) < 100:  # Filter out very short or long matches
                        if match not in insights["top_attractions"]:
                            insights["top_attractions"].append(match.strip())
        
        # Extract activities
        for keyword in activity_keywords:
            if keyword.lower() in combined_text:
                activity_pattern = rf'(?:กิจกรรม|activities|ทำ|do|experience|adventure)\s?[:-]?\s?([^\n.,]+)'
                matches = re.findall(activity_pattern, combined_text, re.IGNORECASE)
                for match in matches:
                    if len(match) > 3 and len(match) < 100:
                        if match not in insights["recommended_activities"]:
                            insights["recommended_activities"].append(match.strip())
        
        # Extract food recommendations
        for keyword in food_keywords:
            if keyword.lower() in combined_text:
                food_pattern = rf'(?:อาหาร|ร้านอาหาร|ของกิน|เมนู|food|restaurant|eat)\s?[:-]?\s?([^\n.,]+)'
                matches = re.findall(food_pattern, combined_text, re.IGNORECASE)
                for match in matches:
                    if len(match) > 3 and len(match) < 100:
                        if match not in insights["food_recommendations"]:
                            insights["food_recommendations"].append(match.strip())
        
        # Extract accommodation tips
        for keyword in accommodation_keywords:
            if keyword.lower() in combined_text:
                accommodation_pattern = rf'(?:ที่พัก|โรงแรม|รีสอร์ท|hotel|resort|stay)\s?[:-]?\s?([^\n.,]+)'
                matches = re.findall(accommodation_pattern, combined_text, re.IGNORECASE)
                for match in matches:
                    if len(match) > 3 and len(match) < 100:
                        if match not in insights["accommodation_tips"]:
                            insights["accommodation_tips"].append(match.strip())
        
        # Extract transportation info
        for keyword in transportation_keywords:
            if keyword.lower() in combined_text:
                transport_pattern = rf'(?:เดินทาง|วิธีไป|transportation|travel|get to)\s?[:-]?\s?([^\n.,]+)'
                matches = re.findall(transport_pattern, combined_text, re.IGNORECASE)
                for match in matches:
                    if len(match) > 3 and len(match) < 100:
                        if match not in insights["transportation_info"]:
                            insights["transportation_info"].append(match.strip())
        
        # Look for local tips in the description
        tip_pattern = r'(?:tips?|เคล็ดลับ|แนะนำ|ควร|ต้อง|should|must|recommend)[:\s]+([^\n.]+)'
        tip_matches = re.findall(tip_pattern, description, re.IGNORECASE)
        for match in tip_matches:
            if len(match) > 10 and len(match) < 150:  # More selective for tips
                if match not in insights["local_tips"]:
                    insights["local_tips"].append(match.strip())
    
    # Limit the number of items per category
    for key in insights:
        if isinstance(insights[key], list) and len(insights[key]) > 10:
            insights[key] = insights[key][:10]
    
    return insights

def format_youtube_insights(insights: Dict[str, Any]) -> str:
    """
    Formats YouTube insights as a readable text.
    
    Args:
        insights: Dictionary containing extracted insights
        
    Returns:
        Formatted insights as a string
    """
    if not insights:
        return "ไม่พบข้อมูลที่เกี่ยวข้องจาก YouTube"
    
    destination = insights.get("destination", "")
    
    formatted_text = f"ข้อมูลจาก YouTube เกี่ยวกับ {destination}:\n\n"
    
    # Add attractions
    if insights.get("top_attractions"):
        formatted_text += "🏛️ สถานที่ท่องเที่ยวที่ได้รับการกล่าวถึง:\n"
        for attraction in insights["top_attractions"]:
            formatted_text += f"- {attraction}\n"
        formatted_text += "\n"
    
    # Add activities
    if insights.get("recommended_activities"):
        formatted_text += "🏄‍♀️ กิจกรรมที่แนะนำ:\n"
        for activity in insights["recommended_activities"]:
            formatted_text += f"- {activity}\n"
        formatted_text += "\n"
    
    # Add food recommendations
    if insights.get("food_recommendations"):
        formatted_text += "🍜 อาหารและร้านอาหารที่แนะนำ:\n"
        for food in insights["food_recommendations"]:
            formatted_text += f"- {food}\n"
        formatted_text += "\n"
    
    # Add accommodation tips
    if insights.get("accommodation_tips"):
        formatted_text += "🏨 ที่พักที่ได้รับการกล่าวถึง:\n"
        for accommodation in insights["accommodation_tips"]:
            formatted_text += f"- {accommodation}\n"
        formatted_text += "\n"
    
    # Add transportation info
    if insights.get("transportation_info"):
        formatted_text += "🚌 ข้อมูลการเดินทาง:\n"
        for transport in insights["transportation_info"]:
            formatted_text += f"- {transport}\n"
        formatted_text += "\n"
    
    # Add local tips
    if insights.get("local_tips"):
        formatted_text += "💡 เคล็ดลับจากคนท้องถิ่น:\n"
        for tip in insights["local_tips"]:
            formatted_text += f"- {tip}\n"
        formatted_text += "\n"
    
    return formatted_text
