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

# Set up formatter for detailed logs
detailed_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Check if we need to add a file handler
if not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
    try:
        file_handler = logging.FileHandler('travel_a2a.log')
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        logger.info("Added file handler for YouTube tool logging")
    except Exception as e:
        logger.warning(f"Could not set up file handler for YouTube logging: {e}")

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
        
        # Log the search request
        logger.info(f"YouTube Search: Querying for '{query}' with max_results={max_results}")
        
        # Execute the search request
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=max_results,
            type='video'
        ).execute()
        
        # Log search response stats
        total_results = search_response.get('pageInfo', {}).get('totalResults', 0)
        logger.info(f"YouTube Search: Found {total_results} total results for '{query}'")
        
        # Process the search results
        videos = []
        logger.info(f"YouTube Search: Processing {len(search_response.get('items', []))} video items")
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
        
        # Log detailed result information
        if videos:
            logger.info(f"YouTube Search Results: Found {len(videos)} videos")
            for i, video in enumerate(videos):
                logger.info(f"  Video {i+1}: '{video['title']}' by {video['channel']} - {video['url']}")
        else:
            logger.warning(f"YouTube Search: No videos found for query '{query}'")
            
        return videos
    
    except HttpError as e:
        error_details = str(e)
        logger.error(f"YouTube Search HTTP Error: {error_details}")
        logger.error(f"Failed YouTube search query: '{query}'")
        return [{"error": f"YouTube API error: {error_details}"}]
    
    except Exception as e:
        error_details = str(e)
        logger.error(f"YouTube Search General Error: {error_details}")
        logger.error(f"Failed YouTube search query: '{query}'")
        return [{"error": f"Error: {error_details}"}]

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
        # Log transcript request
        logger.info(f"YouTube Transcript: Requesting transcript for video_id: {video_id} in language: {language}")
        
        # Extract the video ID if a full URL was provided
        if "youtube.com" in video_id or "youtu.be" in video_id:
            original_id = video_id
            video_id = extract_video_id(video_id)
            logger.info(f"YouTube Transcript: Extracted video_id '{video_id}' from URL '{original_id}'")
        
        # Get available transcript list
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to get transcript with specified language
        try:
            logger.info(f"YouTube Transcript: Retrieving transcript list for video {video_id}")
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            logger.info(f"YouTube Transcript: Searching for transcript in language: {language}")
            transcript = transcript_list.find_transcript([language])
            
            logger.info(f"YouTube Transcript: Found transcript in {transcript.language_code}, fetching data")
            transcript_data = transcript.fetch()
            
            # Process transcript data
            full_text = " ".join([item['text'] for item in transcript_data])
            word_count = len(full_text.split())
            duration = transcript_data[-1]['start'] + transcript_data[-1]['duration'] if transcript_data else 0
            
            # Create result dictionary
            result = {
                "video_id": video_id,
                "language": transcript.language_code,
                "transcript": transcript_data,
                "full_text": full_text,
                "word_count": word_count,
                "duration_seconds": duration,
                "success": True
            }
            
            # Log successful transcript retrieval details
            logger.info(f"YouTube Transcript: Successfully retrieved transcript for video {video_id}")
            logger.info(f"YouTube Transcript Details: Language={transcript.language_code}, Words={word_count}, Duration={duration}s")
            
            return result
        
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            error_details = str(e)
            logger.warning(f"YouTube Transcript Error: No transcript available for video {video_id}: {error_details}")
            return {
                "video_id": video_id,
                "error": error_details,
                "success": False,
                "error_type": "no_transcript"
            }
        
        except Exception as e:
            error_details = str(e)
            logger.error(f"YouTube Transcript General Error: Failed to retrieve transcript for video {video_id}: {error_details}")
            return {
                "video_id": video_id,
                "error": error_details,
                "success": False,
                "error_type": "general_error"
            }
    
    except Exception as e:
        error_details = str(e)
        logger.error(f"YouTube Transcript General Error: Failed to retrieve transcript for video {video_id}: {error_details}")
        return {
            "video_id": video_id,
            "error": error_details,
            "success": False,
            "error_type": "general_error"
        }

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
