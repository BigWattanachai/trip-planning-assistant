"""
YouTube API wrapper for Travel A2A Backend.
This module provides basic YouTube search and transcription functionality.
"""

import os
import logging
from typing import Dict, List, Any, Optional
import re
from dotenv import load_dotenv

# Load environment variables if not already loaded
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Try to import YouTube API libraries
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
    YOUTUBE_AVAILABLE = True
    logger.info("YouTube API libraries successfully imported")
except ImportError as e:
    logger.warning(f"YouTube API libraries not available: {e}")
    YOUTUBE_AVAILABLE = False

# YouTube API key from environment variable
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def search_videos(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search for YouTube videos matching the given query.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        List of dictionaries with video information
        
    Example:
        >>> search_videos("Bangkok travel guide")
        [
            {
                "id": "video_id_1",
                "title": "Ultimate Bangkok Travel Guide 2025",
                "channel": "Travel With Me",
                "published_at": "2025-01-15T12:00:00Z",
                "description": "Explore the best places to visit in Bangkok...",
                "thumbnail_url": "https://i.ytimg.com/vi/video_id_1/hqdefault.jpg"
            },
            ...
        ]
    """
    if not YOUTUBE_API_KEY or not YOUTUBE_AVAILABLE:
        logger.error("YouTube API key not found or YouTube API not available")
        return [{"error": "YouTube API not available or not configured"}]
    
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        # Execute the search request
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=max_results,
            type='video'
        ).execute()
        
        # Process the search results
        videos = []
        for item in search_response.get('items', []):
            if item.get('id', {}).get('kind') == 'youtube#video':
                video_id = item['id']['videoId']
                snippet = item.get('snippet', {})
                
                videos.append({
                    'id': video_id,
                    'title': snippet.get('title', ''),
                    'channel': snippet.get('channelTitle', ''),
                    'published_at': snippet.get('publishedAt', ''),
                    'description': snippet.get('description', ''),
                    'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                })
        
        return videos
    
    except HttpError as e:
        logger.error(f"An HTTP error occurred during YouTube search: {e}")
        return [{"error": f"YouTube API error: {str(e)}"}]
    
    except Exception as e:
        logger.error(f"An error occurred during YouTube search: {e}")
        return [{"error": f"Error: {str(e)}"}]

def get_transcript(video_id: str, language: str = 'en') -> Dict[str, Any]:
    """
    Get the transcript of a YouTube video.
    
    Args:
        video_id: The YouTube video ID
        language: Preferred language code (default: 'en')
        
    Returns:
        Dictionary with transcript information
        
    Example:
        >>> get_transcript("video_id_1")
        {
            "video_id": "video_id_1",
            "language": "en",
            "transcript": "Welcome to Bangkok, the capital city of Thailand...",
            "segments": [
                {"start": 0.0, "text": "Welcome to Bangkok"},
                {"start": 3.5, "text": "the capital city of Thailand"},
                ...
            ]
        }
    """
    if not YOUTUBE_AVAILABLE:
        logger.error("YouTube transcript API not available")
        return {"error": "YouTube transcript API not available"}
    
    try:
        # Extract video ID from URL if a full URL was provided
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
        
        # Get available transcript list
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to find transcript in the preferred language, or fall back to available languages
        try:
            transcript = transcript_list.find_transcript([language])
        except NoTranscriptFound:
            try:
                # Get any available transcript and translate it
                transcript = transcript_list.find_transcript(['en', 'de', 'fr', 'es', 'it'])
                transcript = transcript.translate(language)
            except NoTranscriptFound:
                # If no preferred languages are found, just get the first available
                transcript = next(transcript_list._transcripts.values().__iter__())
        
        # Get the transcript data
        transcript_data = transcript.fetch()
        
        # Combine the text into a full transcript
        full_transcript = " ".join([item.get('text', '') for item in transcript_data])
        
        return {
            "video_id": video_id,
            "language": transcript.language,
            "transcript": full_transcript,
            "segments": transcript_data
        }
    
    except TranscriptsDisabled:
        logger.warning(f"Transcripts are disabled for video {video_id}")
        return {"error": "Transcripts are disabled for this video"}
    
    except NoTranscriptFound:
        logger.warning(f"No transcript found for video {video_id}")
        return {"error": "No transcript found for this video"}
    
    except Exception as e:
        logger.error(f"An error occurred while getting transcript: {e}")
        return {"error": f"Error: {str(e)}"}

# For local testing
if __name__ == "__main__":
    # Test search_videos
    results = search_videos("Thailand travel guide")
    print(f"Found {len(results)} videos")
    for video in results:
        print(f"Title: {video.get('title')}")
        print(f"URL: {video.get('url')}")
        print("---")
    
    # Test get_transcript if videos were found
    if results and 'id' in results[0]:
        transcript = get_transcript(results[0]['id'])
        if 'error' not in transcript:
            print(f"Transcript (first 100 chars): {transcript.get('transcript', '')[:100]}...")
        else:
            print(f"Transcript error: {transcript.get('error')}")
