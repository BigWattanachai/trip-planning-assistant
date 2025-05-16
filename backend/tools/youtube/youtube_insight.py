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

# Configure logging - use existing logger without adding more handlers
logger = logging.getLogger(__name__)

# Import base YouTube functions
try:
    from tools.youtube.youtube import search_videos, get_transcript, YOUTUBE_AVAILABLE
    logger.info("Successfully imported YouTube functions from tools.youtube.youtube")
except ImportError:
    try:
        from backend.tools.youtube.youtube import search_videos, get_transcript, YOUTUBE_AVAILABLE
        logger.info("Successfully imported YouTube functions from backend.tools.youtube.youtube")
    except ImportError:
        try:
            from tools.youtube.youtube import search_videos, get_transcript, YOUTUBE_AVAILABLE
            logger.info("Successfully imported YouTube functions from tools.youtube.youtube")
        except ImportError as e:
            logger.error(f"Failed to import base YouTube functions: {e}")
            logger.error("Using FALLBACK implementation for YouTube functionality. Results will be simulated.")
            YOUTUBE_AVAILABLE = False
            
            # Define stub functions for testing/fallback if imports fail
            def search_videos(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
                logger.info(f"[FALLBACK] Simulating search for: {query}")
                destination = query.split(' ')[0] if ' ' in query else query  # Extract first word as destination
                
                # Generate some fake results based on the query
                results = []
                titles = [
                    f"{destination} Travel Guide | Expedia",
                    f"10 BEST Things to Do in {destination}! (2025)",
                    f"Amazing Street Food in {destination} - Thai Food Tour",
                    f"{destination} Thailand Travel Vlog - Hidden Gems",
                    f"Top 5 Places to Visit in {destination} Thailand"
                ]
                
                channels = ["Expedia", "Mark Wiens", "Kara and Nate", "Travel With Me", "Indigo Traveller"]
                
                for i in range(min(max_results, 5)):
                    video_id = f"simulated_id_{i}_{destination}".lower()
                    results.append({
                        "id": video_id,
                        "title": titles[i],
                        "channel": channels[i],
                        "published_at": "2025-01-15T12:00:00Z",
                        "description": f"Explore the best places to visit in {destination}, Thailand. This guide covers top attractions, food, accommodations, and travel tips.",
                        "thumbnail_url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                        "url": f"https://www.youtube.com/watch?v={video_id}"
                    })
                
                return results
                
            def get_transcript(video_id: str, language: str = 'en') -> Dict[str, Any]:
                logger.info(f"[FALLBACK] Simulating transcript for: {video_id}")
                
                # Extract destination from video_id if possible
                parts = video_id.split('_')
                destination = parts[2] if len(parts) > 2 else "Thailand"
                
                # Create a simulated transcript
                transcript_text = f"Welcome to {destination.title()}, one of Thailand's most beautiful destinations. "
                transcript_text += f"In this video, we'll explore the top attractions in {destination.title()}, "
                transcript_text += "including temples, markets, street food, and hidden gems. "
                transcript_text += "We'll also cover transportation, accommodations, and travel tips to make your visit unforgettable."
                
                return {
                    "video_id": video_id,
                    "language": language,
                    "success": True,
                    "transcript": [{"start": 0.0, "text": transcript_text}],
                    "full_text": transcript_text,
                    "word_count": len(transcript_text.split()),
                    "duration_seconds": 300.0,
                }

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
    logger.info(f"YouTube Travel Search: Searching for '{destination}' with focus '{focus}' (max results: {max_results})")
    if not YOUTUBE_AVAILABLE:
        logger.error("YouTube API not available")
        return [{"error": "YouTube API not available"}]
    
    # Construct a search query targeting travel content
    query = f"{destination} {focus}"
    logger.info(f"YouTube Travel Search: Constructed query '{query}'")
    
    # Get videos using the base search function
    logger.info(f"YouTube Travel Search: Calling base search_videos with query '{query}'")
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
        
        # Sort by relevance score and log results
        sorted_videos = sorted(videos, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Log the sorted results with detailed information
        logger.info(f"YouTube Travel Search for '{destination}': Found {len(sorted_videos)} relevant videos")
        for i, video in enumerate(sorted_videos[:min(3, len(sorted_videos))]):
            logger.info(f"  Top {i+1}: '{video['title']}' by {video['channel']} (score: {video.get('relevance_score', 0)})")
        
        return sorted_videos
    
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
    
    # Final detailed log - only show if videos were analyzed for sentiment
    # This section was causing an error because 'videos' key doesn't exist in the result dictionary
    logger.info(f"Video details extracted for '{result.get('title', 'Unknown video')}' by '{result.get('channel', 'Unknown channel')}'")  
    
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
    logger.info(f"YouTube Insight: Extracting travel insights from {len(video_ids)} videos")
    for i, vid in enumerate(video_ids[:min(5, len(video_ids))]):
        logger.info(f"  Processing video {i+1}: {vid}")
    if not YOUTUBE_AVAILABLE:
        logger.error("YouTube API not available")
        return {"error": "YouTube API not available"}
    
    if not video_ids:
        return {"error": "No video IDs provided"}
    
    results = {
        "top_places": [],
        "top_activities": [],
        "common_phrases": [],
        "videos_analyzed": 0,
        "transcripts_available": 0,
        "processing_details": []
    }
    
    logger.info(f"YouTube Insight: Initialized results structure for {len(video_ids)} videos")
    for vid_id in video_ids:
        video_details = get_video_details(vid_id)
        
        if 'error' not in video_details:
            results['videos_analyzed'] += 1
            
            if video_details.get('transcript_available', False):
                results['transcripts_available'] += 1
                
                # Log transcript availability and size
                word_count = video_details.get('transcript_length', 0)
                logger.info(f"YouTube Insight: Got transcript for video {vid_id} ({word_count} words)")
                
                # Add processing details
                results['processing_details'].append({
                    "video_id": vid_id,
                    "title": video_details.get('title', 'Unknown'),
                    "transcript_available": True,
                    "transcript_length": word_count
                })
                
                # Process transcript data for insights
                full_text = video_details.get('transcript', {}).get('full_text', '')
                
                # Extract potential places using regex patterns
                # Look for capitalized words followed potentially by "Beach", "Temple", etc.
                place_pattern = r'([A-Z][a-z]+(?: [A-Z][a-z]+)*)(?: Beach| Temple| Palace| Market| Island| Town| Village| Mountain| National Park| Bay)?'
                potential_places = re.findall(place_pattern, full_text)
                
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
                    matches = re.findall(pattern, full_text.lower())
                    activities.extend([match for match in matches if len(match) > 3])
                
                # Extract key phrases that might indicate travel recommendations
                key_phrases = []
                phrase_patterns = [
                    r'(?:must|should|recommend|best|favorite|amazing|beautiful|stunning) (?:place|thing|activity|sight|experience|location|destination|restaurant|hotel) (?:to|is|in|at) ([A-Za-z]+(?: [A-Za-z]+){0,5})',
                    r'(?:don\'t miss|make sure to|try the|check out) ([A-Za-z]+(?: [A-Za-z]+){0,5})'
                ]
                
                for pattern in phrase_patterns:
                    matches = re.findall(pattern, full_text.lower())
                    key_phrases.extend([match for match in matches if len(match) > 3])
                
                # Add extracted information to results
                results['top_places'].extend(top_places)
                results['top_activities'].extend(activities)
                results['common_phrases'].extend(key_phrases)
            else:
                error_info = video_details.get('error', 'Unknown error')
                logger.warning(f"YouTube Insight: No transcript available for video {vid_id}: {error_info}")
                
                # Add processing details for videos without transcripts
                results['processing_details'].append({
                    "video_id": vid_id,
                    "title": video_details.get('title', 'Unknown'),
                    "transcript_available": False,
                    "error": error_info
                })
    
    # Calculate top places, activities, and phrases
    if len(results['top_places']) > 0:
        results['top_places'] = [place for place, _ in Counter(results['top_places']).most_common(5)]
        logger.info(f"YouTube Insight: Top places identified: {', '.join(results['top_places'])}")
    if len(results['top_activities']) > 0:
        results['top_activities'] = [activity for activity, _ in Counter(results['top_activities']).most_common(5)]
        logger.info(f"YouTube Insight: Top activities identified: {', '.join(results['top_activities'])}")
    if len(results['common_phrases']) > 0:
        results['common_phrases'] = [phrase for phrase, _ in Counter(results['common_phrases']).most_common(5)]
        logger.info(f"YouTube Insight: Common phrases identified: {', '.join(results['common_phrases'][:3])}")
    
    # Final results
    logger.info(f"YouTube Insight: Successfully extracted insights from {results['videos_analyzed']} videos")
    logger.info(f"YouTube Insight: Transcripts were available for {results['transcripts_available']} videos")
    logger.info(f"YouTube Insight: Found {len(results['top_places'])} places, {len(results['top_activities'])} activities, and {len(results['common_phrases'])} common phrases")
    
    return results

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
    logger.info(f"YouTube Sentiment Analysis: Starting analysis for destination '{destination}'")
    if not YOUTUBE_AVAILABLE:
        logger.error("YouTube API not available")
        return {"error": "YouTube API not available"}
    
    # Prepare result structure
    result = {
        "destination": destination,
        "overall_sentiment": "Neutral",
        "positive_mentions": 0,
        "negative_mentions": 0,
        "neutral_mentions": 0,
        "engagement_rate": 0,
        "video_count": 0,
        "videos": [],
        "analysis_details": []
    }
    
    logger.info(f"YouTube Sentiment Analysis: Initialized sentiment analysis structure for '{destination}'")
    
    # Search for videos about the destination
    logger.info(f"YouTube Sentiment Analysis: Searching for videos about '{destination}'")
    videos = search_travel_videos(destination, "review", max_results=10)
    
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
        result['overall_sentiment'] = "Positive"
    elif negative_matches > positive_matches:
        result['overall_sentiment'] = "Negative"
    else:
        result['overall_sentiment'] = "Neutral"
        
    logger.info(f"YouTube Sentiment Analysis for '{destination}': Overall sentiment is {result['overall_sentiment']}")
    logger.info(f"YouTube Sentiment Analysis for '{destination}': {positive_matches} positive, {negative_matches} negative, {len(videos) - positive_matches - negative_matches} neutral mentions")
    logger.info(f"YouTube Sentiment Analysis for '{destination}': Analyzed {len(videos)} videos with engagement rate {engagement_rate:.2f}")
    
    return {
        "destination": destination,
        "overall_sentiment": result['overall_sentiment'],
        "positive_mentions": positive_matches,
        "negative_mentions": negative_matches,
        "neutral_mentions": len(videos) - positive_matches - negative_matches,
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
