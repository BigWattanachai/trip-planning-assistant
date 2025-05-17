"""
YouTube API wrapper for Trip Planning Assistant Backend.
This module provides basic YouTube search and transcription functionality.
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional
import re
from dotenv import load_dotenv

# Fix module import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, '../..'))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)
    print(f"Added {backend_dir} to sys.path")

# Load environment variables if not already loaded
load_dotenv()

# Logging: Use only the app-level logging configuration.
# Do NOT add handlers or set log file path here. Just get the module logger.
logger = logging.getLogger(__name__)

# (Do not set level or add handlers here. App-level config will handle it.)

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
    # Log start of search with clear markers
    logger.info(f"====== YOUTUBE SEARCH REQUEST ======")
    logger.info(f"Search Query: '{query}'")
    logger.info(f"Max Results: {max_results}")
    logger.info(f"YouTube API Available: {YOUTUBE_AVAILABLE}")
    logger.info(f"YouTube API Key Set: {bool(YOUTUBE_API_KEY)}")
    
    if not YOUTUBE_API_KEY or not YOUTUBE_AVAILABLE:
        error_msg = "YouTube API key not found or YouTube API not available"
        logger.error(error_msg)
        if not YOUTUBE_API_KEY:
            logger.error("Please set YOUTUBE_API_KEY environment variable")
        if not YOUTUBE_AVAILABLE:
            logger.error("Required libraries not installed. Install googleapiclient and youtube_transcript_api")
        logger.info(f"====== YOUTUBE SEARCH FAILED ======")
        return [{"error": error_msg}]
    
    try:
        logger.info(f"Initializing YouTube API client...")
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        logger.info(f"YouTube API client initialized successfully")
        
        # Execute the search request with detailed logging
        logger.info(f"Executing search request for query: '{query}'")
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=max_results,
            type='video',
            relevanceLanguage='th',  # Prioritize Thai content for travel in Thailand
        ).execute()
        
        # Log search response stats in detail
        total_results = search_response.get('pageInfo', {}).get('totalResults', 0)
        results_per_page = search_response.get('pageInfo', {}).get('resultsPerPage', 0)
        next_page_token = search_response.get('nextPageToken', 'None')
        logger.info(f"Search response metadata:")
        logger.info(f"  Total results: {total_results}")
        logger.info(f"  Results per page: {results_per_page}")
        logger.info(f"  Next page token: {next_page_token}")
        
        # Process the search results with better logging
        items = search_response.get('items', [])
        logger.info(f"Processing {len(items)} video items from response")
        
        videos = []
        for idx, item in enumerate(items):
            try:
                if item.get('id', {}).get('kind') == 'youtube#video':
                    video_id = item['id']['videoId']
                    snippet = item.get('snippet', {})
                    
                    video_data = {
                        'id': video_id,
                        'title': snippet.get('title', ''),
                        'channel': snippet.get('channelTitle', ''),
                        'published_at': snippet.get('publishedAt', ''),
                        'description': snippet.get('description', ''),
                        'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                        'url': f"https://www.youtube.com/watch?v={video_id}"
                    }
                    videos.append(video_data)
                    logger.info(f"  Processed video {idx+1}: ID={video_id}, Title='{snippet.get('title', '')}', Channel='{snippet.get('channelTitle', '')}', Published={snippet.get('publishedAt', '')}")
                else:
                    logger.warning(f"  Item {idx+1} is not a video (kind: {item.get('id', {}).get('kind')})")
            except KeyError as ke:
                logger.error(f"  KeyError processing video {idx+1}: {ke}")
            except Exception as e:
                logger.error(f"  Error processing video {idx+1}: {e}")
        
        # Log detailed result information
        if videos:
            logger.info(f"Search results summary: Found {len(videos)} videos")
            for i, video in enumerate(videos):
                logger.info(f"  Result {i+1}: '{video['title']}' by {video['channel']} - {video['url']}")
        else:
            logger.warning(f"No videos found for query '{query}'")
        
        logger.info(f"====== YOUTUBE SEARCH COMPLETE ======")
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

def get_transcript(video_id: str, language: str = 'th') -> Dict[str, Any]:
    """
    Get the transcript of a YouTube video, prioritizing Thai ('th') and falling back to English ('en') if not available.
    
    Args:
        video_id: The YouTube video ID
        language: Preferred language code (default: 'th')
        
    Returns:
        Dictionary with transcript information
        
    Example:
        >>> get_transcript("video_id_1")
        {
            "video_id": "video_id_1",
            "language": "th",
            "transcript": "...",
            "segments": [
                {"start": 0.0, "text": "..."},
                ...
            ]
        }
    """
    if not YOUTUBE_AVAILABLE:
        logger.error("YouTube transcript API not available")
        return {"error": "YouTube transcript API not available"}
    
    if not YOUTUBE_API_KEY:
        logger.error("YouTube API key is not set. Please set YOUTUBE_API_KEY environment variable.")
        return {"error": "YouTube API key not configured"}
    
    try:
        logger.info(f"====== YOUTUBE TRANSCRIPT REQUEST ======")
        logger.info(f"Video ID: {video_id}")
        logger.info(f"Requested Language: {language}")
        logger.info(f"YouTube API Available: {YOUTUBE_AVAILABLE}")
        
        # Extract the video ID if a full URL was provided
        if "youtube.com" in video_id or "youtu.be" in video_id:
            original_id = video_id
            video_id = extract_video_id(video_id)
            logger.info(f"Extracted video_id '{video_id}' from URL '{original_id}'")
        
        logger.info(f"Attempting to get transcript list for video {video_id}...")
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            try:
                if hasattr(transcript_list, '_transcripts'):
                    available_languages = [t.language_code for t in transcript_list._transcripts.values()]
                else:
                    available_languages = ["en"]
                    try:
                        all_transcripts = list(transcript_list)
                        available_languages = [t.language_code for t in all_transcripts]
                    except Exception:
                        pass
                logger.info(f"Available transcripts: {available_languages}")
            except Exception as lang_err:
                logger.warning(f"Could not determine available languages: {lang_err}")
                logger.info("Continuing with transcript fetch anyway...")
        except Exception as e:
            logger.error(f"Error listing transcripts: {str(e)}")
            return {"error": f"Failed to list transcripts: {str(e)}", "video_id": video_id}
        
        # Try preferred languages: Thai first, then English
        preferred_languages = [language, 'en'] if language != 'en' else [language]
        last_exception = None
        for lang_code in preferred_languages:
            try:
                logger.info(f"Searching for transcript in language: {lang_code}")
                transcript = transcript_list.find_transcript([lang_code])
                logger.info(f"Found transcript in {transcript.language_code}, fetching data")
                try:
                    transcript_data = transcript.fetch()
                    if not transcript_data or not isinstance(transcript_data, list):
                        logger.warning(f"Retrieved transcript data is empty or invalid: {type(transcript_data)}")
                        logger.info("Attempting to use YouTubeTranscriptApi.get_transcript directly...")
                        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang_code])
                except Exception as fetch_err:
                    logger.warning(f"Error fetching transcript with .fetch(): {fetch_err}")
                    logger.info("Attempting to use YouTubeTranscriptApi.get_transcript directly...")
                    transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang_code])
                logger.info(f"Successfully fetched transcript in language: {lang_code}")
                return {
                    "video_id": video_id,
                    "language": lang_code,
                    "success": True,
                    "transcript": transcript_data,
                    "full_text": " ".join([seg.get('text', '') for seg in transcript_data]),
                    "word_count": sum(len(seg.get('text', '').split()) for seg in transcript_data),
                    "duration_seconds": transcript_data[-1]['start'] + transcript_data[-1].get('duration', 0) if transcript_data else 0,
                }
            except Exception as transcript_err:
                logger.warning(f"Transcript not found for language '{lang_code}': {transcript_err}")
                last_exception = transcript_err
                continue
        logger.error(f"YouTube Transcript Error: No transcript available for video {video_id}: {last_exception}")
        return {"error": f"Could not retrieve a transcript for the video https://www.youtube.com/watch?v={video_id}! This is most likely caused by:\n\nNo transcripts were found for any of the requested language codes: {preferred_languages}", "video_id": video_id}
    except Exception as outer_err:
        logger.error(f"Unexpected error getting transcript for video {video_id}: {outer_err}")
        return {"error": f"Unexpected error: {outer_err}", "video_id": video_id}
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
