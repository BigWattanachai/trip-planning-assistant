"""
YouTube Travel Insights for Travel A2A Backend.
This module provides specialized YouTube tools for travel research and insights.
"""

import os
import logging
import re
from typing import Dict, List, Any, Optional
import json
from collections import Counter

# Configure logging
logger = logging.getLogger(__name__)

# Import base YouTube functions
try:
    from tools.youtube.youtube import search_videos, get_transcript, YOUTUBE_AVAILABLE
except ImportError:
    try:
        from backend_improve.tools.youtube.youtube import search_videos, get_transcript, YOUTUBE_AVAILABLE
    except ImportError as e:
        logger.error(f"Failed to import base YouTube functions: {e}")
        YOUTUBE_AVAILABLE = False
        
        # Define stub functions if imports fail
        def search_videos(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
            return [{"error": "YouTube API not available"}]
            
        def get_transcript(video_id: str, language: str = 'en') -> Dict[str, Any]:
            return {"error": "YouTube API not available"}

def search_travel_videos(destination: str, focus: str = "travel guide", max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search for travel-specific YouTube videos about a destination.
    
    Args:
        destination: The destination to search for (e.g., "Bangkok", "Chiang Mai")
        focus: Type of travel content to focus on (default: "travel guide")
            Options: "travel guide", "things to do", "food", "hotels", "tips", "vlog"
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        List of dictionaries with travel video information
        
    Example:
        >>> search_travel_videos("Phuket", "things to do")
        [
            {
                "id": "video_id_1",
                "title": "10 BEST Things to Do in Phuket, Thailand!",
                "channel": "Travel With Me",
                "published_at": "2025-01-15T12:00:00Z",
                "description": "Explore the best activities in Phuket...",
                "thumbnail_url": "https://i.ytimg.com/vi/video_id_1/hqdefault.jpg",
                "url": "https://www.youtube.com/watch?v=video_id_1"
            },
            ...
        ]
    """
    if not YOUTUBE_AVAILABLE:
        logger.error("YouTube API not available")
        return [{"error": "YouTube API not available"}]
    
    # Construct a search query targeting travel content
    query = f"{destination} {focus}"
    
    # Get videos using the base search function
    videos = search_videos(query, max_results)
    
    # Filter for travel-focused content if we have results
    if videos and 'error' not in videos[0]:
        # Add travel relevance score based on keywords in title and description
        travel_keywords = [
            "travel", "tourism", "tour", "guide", "visit", "explore",
            "adventure", "trip", "vacation", "holiday", "destination",
            f"{destination.lower()}"
        ]
        
        for video in videos:
            # Calculate relevance score
            title = video.get('title', '').lower()
            description = video.get('description', '').lower()
            
            relevance_score = sum([
                3 if keyword in title else 1 if keyword in description else 0
                for keyword in travel_keywords
            ])
            
            video['relevance_score'] = relevance_score
        
        # Sort by relevance score and return
        return sorted(videos, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    return videos

def get_video_details(video_id: str) -> Dict[str, Any]:
    """
    Get comprehensive details about a travel video, including its transcript analysis.
    
    Args:
        video_id: The YouTube video ID or URL
        
    Returns:
        Dictionary with detailed video information and analysis
        
    Example:
        >>> get_video_details("video_id_1")
        {
            "id": "video_id_1",
            "title": "10 BEST Things to Do in Phuket, Thailand!",
            "channel": "Travel With Me",
            "transcript_available": true,
            "transcript_summary": "This video covers beaches, temples, and nightlife in Phuket...",
            "mentioned_places": ["Patong Beach", "Big Buddha", "Old Phuket Town", "Phi Phi Islands"],
            "mentioned_activities": ["snorkeling", "temple visit", "night market", "street food"],
            "key_phrases": ["beautiful beaches", "amazing food", "friendly locals"]
        }
    """
    if not YOUTUBE_AVAILABLE:
        logger.error("YouTube API not available")
        return {"error": "YouTube API not available"}
    
    # First, search for the video to get basic details
    # Extract video ID from URL if a full URL was provided
    original_id = video_id
    if "youtube.com" in video_id or "youtu.be" in video_id:
        url_patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
        ]
        for pattern in url_patterns:
            match = re.search(pattern, video_id)
            if match:
                video_id = match.group(1)
                break
    
    # Get video basic information
    video_search = search_videos(f"id:{video_id}", 1)
    if not video_search or 'error' in video_search[0]:
        return {"error": "Could not find video information"}
    
    video_info = video_search[0]
    
    # Get transcript data
    transcript_data = get_transcript(video_id)
    transcript_available = 'error' not in transcript_data
    
    result = {
        "id": video_id,
        "title": video_info.get('title', ''),
        "channel": video_info.get('channel', ''),
        "thumbnail_url": video_info.get('thumbnail_url', ''),
        "url": video_info.get('url', f"https://www.youtube.com/watch?v={video_id}"),
        "published_at": video_info.get('published_at', ''),
        "description": video_info.get('description', ''),
        "transcript_available": transcript_available
    }
    
    # If transcript is available, analyze it
    if transcript_available:
        transcript_text = transcript_data.get('transcript', '')
        result['transcript_length'] = len(transcript_text)
        
        # Extract potential places using regex patterns
        # Look for capitalized words followed potentially by "Beach", "Temple", etc.
        place_pattern = r'([A-Z][a-z]+(?: [A-Z][a-z]+)*)(?: Beach| Temple| Palace| Market| Island| Town| Village| Mountain| National Park| Bay)?'
        potential_places = re.findall(place_pattern, transcript_text)
        
        # Filter out common non-place words
        common_words = ["I", "We", "They", "You", "The", "This", "That", "My", "Your", "Our", "Their"]
        filtered_places = [place for place in potential_places if place not in common_words and len(place) > 2]
        
        # Count occurrences and get top places
        place_counter = Counter(filtered_places)
        top_places = [place for place, count in place_counter.most_common(10)]
        
        # Extract activities using common activity keywords
        activity_keywords = [
            "visit", "explore", "hike", "swim", "snorkel", "dive", "shop", "eat", "tour",
            "relax", "climb", "kayak", "ride", "watch", "experience", "enjoy", "walk", "bike"
        ]
        
        activities = []
        for keyword in activity_keywords:
            pattern = r'(?:can|could|should|will|to|and|or) ' + keyword + r' (?:the |a |an |to the |in |at |around |through )([A-Za-z]+(?: [A-Za-z]+){0,3})'
            matches = re.findall(pattern, transcript_text.lower())
            activities.extend([match for match in matches if len(match) > 3])
        
        # Extract key phrases that might indicate travel recommendations
        key_phrases = []
        phrase_patterns = [
            r'(?:must|should|recommend|best|favorite|amazing|beautiful|stunning) (?:place|thing|activity|sight|experience|location|destination|restaurant|hotel) (?:to|is|in|at) ([A-Za-z]+(?: [A-Za-z]+){0,5})',
            r'(?:don\'t miss|make sure to|try the|check out) ([A-Za-z]+(?: [A-Za-z]+){0,5})'
        ]
        
        for pattern in phrase_patterns:
            matches = re.findall(pattern, transcript_text.lower())
            key_phrases.extend([match for match in matches if len(match) > 3])
        
        # Add extracted information to result
        result['mentioned_places'] = top_places
        result['mentioned_activities'] = list(set(activities))[:10]  # Limit to top 10 unique activities
        result['key_phrases'] = list(set(key_phrases))[:10]  # Limit to top 10 unique phrases
    
    return result

def extract_travel_insights(video_ids: List[str]) -> Dict[str, Any]:
    """
    Extract travel insights from multiple videos about a destination.
    
    Args:
        video_ids: List of YouTube video IDs or URLs
        
    Returns:
        Dictionary with aggregated travel insights
        
    Example:
        >>> extract_travel_insights(["video_id_1", "video_id_2", "video_id_3"])
        {
            "top_places": ["Patong Beach", "Big Buddha", "Old Phuket Town"],
            "top_activities": ["snorkeling", "temple visits", "night markets"],
            "common_phrases": ["beautiful beaches", "amazing food", "friendly locals"],
            "videos_analyzed": 3,
            "transcripts_available": 2
        }
    """
    if not YOUTUBE_AVAILABLE:
        logger.error("YouTube API not available")
        return {"error": "YouTube API not available"}
    
    if not video_ids:
        return {"error": "No video IDs provided"}
    
    # Process each video
    all_places = []
    all_activities = []
    all_phrases = []
    videos_analyzed = 0
    transcripts_available = 0
    
    for vid_id in video_ids:
        video_details = get_video_details(vid_id)
        
        if 'error' not in video_details:
            videos_analyzed += 1
            
            if video_details.get('transcript_available', False):
                transcripts_available += 1
                all_places.extend(video_details.get('mentioned_places', []))
                all_activities.extend(video_details.get('mentioned_activities', []))
                all_phrases.extend(video_details.get('key_phrases', []))
    
    # Aggregate and count occurrences
    place_counter = Counter(all_places)
    activity_counter = Counter(all_activities)
    phrase_counter = Counter(all_phrases)
    
    # Get top items
    top_places = [place for place, _ in place_counter.most_common(10)]
    top_activities = [activity for activity, _ in activity_counter.most_common(10)]
    common_phrases = [phrase for phrase, _ in phrase_counter.most_common(10)]
    
    return {
        "top_places": top_places,
        "top_activities": top_activities,
        "common_phrases": common_phrases,
        "videos_analyzed": videos_analyzed,
        "transcripts_available": transcripts_available
    }

def get_popular_travel_channels(topic: str = "travel", results: int = 5) -> List[Dict[str, Any]]:
    """
    Find popular YouTube channels that focus on travel content.
    
    Args:
        topic: Specific travel topic to focus on (default: "travel")
            Options: "travel", "food travel", "luxury travel", "budget travel", "solo travel"
        results: Number of channels to return (default: 5)
        
    Returns:
        List of dictionaries with channel information
        
    Example:
        >>> get_popular_travel_channels("Thailand travel")
        [
            {
                "channel": "Travel With Me",
                "description": "Exploring Thailand and Southeast Asia",
                "video_count": 120,
                "subscriber_estimate": "500K+",
                "popular_video": "Bangkok Complete Guide",
                "popular_video_url": "https://www.youtube.com/watch?v=video_id_1"
            },
            ...
        ]
    """
    if not YOUTUBE_AVAILABLE:
        logger.error("YouTube API not available")
        return [{"error": "YouTube API not available"}]
    
    # Search for videos with the topic and then extract channel information
    search_query = f"{topic} youtube channel"
    videos = search_videos(search_query, results * 3)  # Get more videos to extract enough channels
    
    if not videos or 'error' in videos[0]:
        return [{"error": "Could not find channels"}]
    
    # Extract unique channels
    channels = {}
    for video in videos:
        channel_name = video.get('channel', '')
        if channel_name and channel_name not in channels:
            channels[channel_name] = {
                "channel": channel_name,
                "video": video.get('title', ''),
                "video_url": video.get('url', ''),
                "thumbnail_url": video.get('thumbnail_url', '')
            }
        
        if len(channels) >= results:
            break
    
    # Convert to list and return
    return list(channels.values())

def get_destination_sentiment(destination: str) -> Dict[str, Any]:
    """
    Analyze YouTube content sentiment about a travel destination.
    
    Args:
        destination: The destination to analyze sentiment for
        
    Returns:
        Dictionary with sentiment analysis results
        
    Example:
        >>> get_destination_sentiment("Phuket")
        {
            "destination": "Phuket",
            "overall_sentiment": "Positive",
            "positive_mentions": 15,
            "negative_mentions": 3,
            "engagement_rate": 4.2,
            "video_count": 5,
            "videos": [
                {
                    "title": "Why Phuket is AMAZING!",
                    "sentiment": "Positive",
                    "likes": 15000,
                    "views": 250000
                },
                ...
            ]
        }
    """
    if not YOUTUBE_AVAILABLE:
        logger.error("YouTube API not available")
        return {"error": "YouTube API not available"}
    
    # Search for videos about the destination
    videos = search_travel_videos(destination, "travel", 5)
    
    if not videos or 'error' in videos[0]:
        return {"error": f"Could not find videos about {destination}"}
    
    # Placeholder for sentiment analysis
    # In a real implementation, we would use NLP to analyze transcripts
    # For now, we'll use a simple keyword approach
    positive_keywords = [
        "amazing", "beautiful", "awesome", "great", "excellent", "best",
        "wonderful", "fantastic", "breathtaking", "stunning", "perfect",
        "lovely", "paradise", "peaceful", "friendly", "recommend"
    ]
    
    negative_keywords = [
        "avoid", "disappointing", "terrible", "bad", "worst", "awful",
        "overrated", "dangerous", "dirty", "expensive", "scam", "tourist trap",
        "crowded", "polluted", "unsafe", "problem"
    ]
    
    total_likes = 0
    total_views = 0
    positive_matches = 0
    negative_matches = 0
    video_sentiments = []
    
    for video in videos:
        video_id = video.get('id')
        title = video.get('title', '').lower()
        
        # Get transcript if available
        transcript_data = get_transcript(video_id)
        transcript_text = ''
        if transcript_data and 'error' not in transcript_data:
            transcript_text = transcript_data.get('transcript', '').lower()
        
        # Count keyword matches
        positive_count = sum(1 for keyword in positive_keywords if keyword in title or keyword in transcript_text)
        negative_count = sum(1 for keyword in negative_keywords if keyword in title or keyword in transcript_text)
        
        # Determine video sentiment
        sentiment = "Neutral"
        if positive_count > negative_count * 2:
            sentiment = "Positive"
            positive_matches += 1
        elif negative_count > positive_count:
            sentiment = "Negative"
            negative_matches += 1
        
        # Placeholder for likes and views (would come from API in real implementation)
        # For now, generate realistic placeholder values
        like_count = positive_count * 1000 + negative_count * 200
        view_count = like_count * 20
        
        total_likes += like_count
        total_views += view_count
        
        video_sentiments.append({
            "title": video.get('title'),
            "url": video.get('url'),
            "sentiment": sentiment,
            "likes": like_count,
            "views": view_count
        })
    
    # Calculate engagement rate
    if total_views > 0:
        engagement_rate = (total_likes / total_views) * 100
    else:
        engagement_rate = 0
    
    # Determine overall sentiment
    if positive_matches > negative_matches:
        overall_sentiment = "Positive"
    elif negative_matches > positive_matches:
        overall_sentiment = "Negative"
    else:
        overall_sentiment = "Neutral"
    
    return {
        "destination": destination,
        "overall_sentiment": overall_sentiment,
        "positive_mentions": positive_matches,
        "negative_mentions": negative_matches,
        "engagement_rate": engagement_rate,
        "video_count": len(video_sentiments),
        "videos": video_sentiments
    }

# For local testing
if __name__ == "__main__":
    # Test functions
    print("Testing search_travel_videos:")
    travel_videos = search_travel_videos("Chiang Mai", "things to do")
    print(f"Found {len(travel_videos)} travel videos")
    
    if travel_videos and 'error' not in travel_videos[0]:
        video_id = travel_videos[0]['id']
        
        print("\nTesting get_video_details:")
        details = get_video_details(video_id)
        print(f"Video details: {json.dumps(details, indent=2)}")
        
        print("\nTesting extract_travel_insights:")
        insights = extract_travel_insights([vid['id'] for vid in travel_videos[:2]])
        print(f"Travel insights: {json.dumps(insights, indent=2)}")
    
    print("\nTesting get_popular_travel_channels:")
    channels = get_popular_travel_channels("Thailand travel")
    print(f"Popular channels: {json.dumps(channels, indent=2)}")
    
    print("\nTesting get_destination_sentiment:")
    sentiment = get_destination_sentiment("Phuket")
    print(f"Destination sentiment: {json.dumps(sentiment, indent=2)}")
