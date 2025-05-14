#!/usr/bin/env python
"""
Test script for YouTube integration in the Travel A2A application.
This will verify if YouTube search and transcript features are working correctly.
"""

import os
import sys
import logging
import json
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('youtube_test.log')
    ]
)
logger = logging.getLogger("youtube_test")

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

def check_api_key():
    """Check if YouTube API key is configured correctly"""
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        logger.error("❌ YOUTUBE_API_KEY environment variable is not set!")
        logger.error("Please add your YouTube API key to the .env file or set it as an environment variable")
        logger.error("Example: YOUTUBE_API_KEY=your_api_key_here")
        return False
    else:
        logger.info(f"✅ YOUTUBE_API_KEY is set (length: {len(api_key)})")
        # Hide most of the key, show only first 4 and last 4 characters
        visible_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "****"
        logger.info(f"API Key: {visible_key}")
        return True

def test_youtube_search():
    """Test YouTube search functionality"""
    logger.info("\n=== TESTING YOUTUBE SEARCH ===")
    try:
        # Import dynamically to ensure we get proper error messages
        logger.info("Importing YouTube search function...")
        
        try:
            from backend.tools.youtube.youtube import search_videos
            logger.info("✅ Successfully imported search_videos from backend.tools.youtube.youtube")
        except ImportError:
            try:
                from tools.youtube.youtube import search_videos
                logger.info("✅ Successfully imported search_videos from tools.youtube.youtube")
            except ImportError as e:
                logger.error(f"❌ Failed to import search_videos: {e}")
                logger.error("Make sure you have installed the required libraries:")
                logger.error("pip install google-api-python-client")
                return False
        
        # Test search
        query = "Bangkok travel guide"
        logger.info(f"Searching for: '{query}'")
        results = search_videos(query, max_results=3)
        
        if not results:
            logger.error("❌ No results returned from search_videos")
            return False
            
        if "error" in results[0]:
            logger.error(f"❌ Error in search results: {results[0]['error']}")
            return False
            
        logger.info(f"✅ Search successful! Found {len(results)} videos")
        for i, video in enumerate(results):
            logger.info(f"  Video {i+1}: {video['title']} by {video['channel']}")
            logger.info(f"  URL: {video['url']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Exception during search test: {e}")
        return False

def test_youtube_transcript():
    """Test YouTube transcript functionality"""
    logger.info("\n=== TESTING YOUTUBE TRANSCRIPT ===")
    try:
        # Import dynamically
        logger.info("Importing YouTube transcript function...")
        try:
            from backend.tools.youtube.youtube import get_transcript
            logger.info("✅ Successfully imported get_transcript from backend.tools.youtube.youtube")
        except ImportError:
            try:
                from tools.youtube.youtube import get_transcript
                logger.info("✅ Successfully imported get_transcript from tools.youtube.youtube")
            except ImportError as e:
                logger.error(f"❌ Failed to import get_transcript: {e}")
                logger.error("Make sure you have installed the required libraries:")
                logger.error("pip install youtube_transcript_api")
                return False
        
        # First search for a video
        try:
            try:
                from backend.tools.youtube.youtube import search_videos
            except ImportError:
                from tools.youtube.youtube import search_videos
                
            logger.info("Finding a video to test transcript...")
            query = "Bangkok travel guide"
            search_results = search_videos(query, max_results=1)
            
            if not search_results or "error" in search_results[0]:
                logger.error("❌ Failed to find a video for transcript test")
                # Use a known video ID as fallback
                video_id = "bCNU9TrZTfk"  # A popular Bangkok travel guide 
                logger.info(f"Using fallback video ID: {video_id}")
            else:
                video_id = search_results[0]["id"]
                logger.info(f"Selected video: {search_results[0]['title']} (ID: {video_id})")
        except Exception as e:
            logger.error(f"❌ Failed to search for a video: {e}")
            # Use fallback
            video_id = "bCNU9TrZTfk"
            logger.info(f"Using fallback video ID: {video_id}")
            
        # Test transcript
        logger.info(f"Getting transcript for video ID: {video_id}")
        transcript_data = get_transcript(video_id)
        
        if "error" in transcript_data:
            logger.error(f"❌ Error getting transcript: {transcript_data['error']}")
            return False
            
        # Print some transcript info
        logger.info(f"✅ Transcript retrieved successfully!")
        if "word_count" in transcript_data:
            logger.info(f"  Word count: {transcript_data['word_count']}")
        if "language" in transcript_data:
            logger.info(f"  Language: {transcript_data['language']}")
        if "duration_seconds" in transcript_data:
            logger.info(f"  Duration: {transcript_data['duration_seconds']} seconds")
            
        # Print a sample from the transcript
        if "transcript" in transcript_data and transcript_data["transcript"]:
            sample_size = min(3, len(transcript_data["transcript"]))
            logger.info(f"  Sample from transcript (first {sample_size} segments):")
            for i in range(sample_size):
                segment = transcript_data["transcript"][i]
                logger.info(f"    {segment.get('start', 0):.1f}s: {segment.get('text', '')}")
                
        return True
        
    except Exception as e:
        logger.error(f"❌ Exception during transcript test: {e}")
        return False

def test_youtube_insight_agent():
    """Test the YouTube Insight Agent functionality"""
    logger.info("\n=== TESTING YOUTUBE INSIGHT AGENT ===")
    try:
        # Import dynamically
        logger.info("Importing YouTube Insight Agent...")
        try:
            from backend.sub_agents.youtube_insight_agent import analyze_destination_from_youtube
            logger.info("✅ Successfully imported analyze_destination_from_youtube")
        except ImportError:
            try:
                from sub_agents.youtube_insight_agent import analyze_destination_from_youtube
                logger.info("✅ Successfully imported analyze_destination_from_youtube from sub_agents")
            except ImportError as e:
                logger.error(f"❌ Failed to import YouTube Insight Agent: {e}")
                return False
        
        # Test agent
        destination = "Bangkok"
        logger.info(f"Analyzing destination: {destination}")
        results = analyze_destination_from_youtube(destination)
        
        if "error" in results:
            logger.error(f"❌ Error from Insight Agent: {results['error']}")
            return False
            
        # Log the results
        logger.info(f"✅ YouTube Insight Agent returned results successfully!")
        logger.info(f"Results keys: {list(results.keys())}")
        
        if "insights" in results:
            insights = results["insights"]
            logger.info(f"Top places: {insights.get('top_places', [])[:5]}")
            logger.info(f"Top activities: {insights.get('top_activities', [])[:5]}")
            
        if "sentiment" in results:
            sentiment = results["sentiment"]
            logger.info(f"Overall sentiment: {sentiment.get('overall_sentiment', 'Unknown')}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Exception testing YouTube Insight Agent: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting YouTube integration tests")
    
    # Check API key first
    if not check_api_key():
        logger.error("API key check failed. Other tests may not work correctly.")
    
    # Run tests
    search_result = test_youtube_search()
    transcript_result = test_youtube_transcript()
    agent_result = test_youtube_insight_agent()
    
    # Print summary
    logger.info("\n=== TEST SUMMARY ===")
    logger.info(f"API Key Check: {'✅ PASSED' if check_api_key() else '❌ FAILED'}")
    logger.info(f"YouTube Search: {'✅ PASSED' if search_result else '❌ FAILED'}")
    logger.info(f"YouTube Transcript: {'✅ PASSED' if transcript_result else '❌ FAILED'}")
    logger.info(f"YouTube Insight Agent: {'✅ PASSED' if agent_result else '❌ FAILED'}")
    
    if not (search_result and transcript_result and agent_result):
        logger.info("\n=== TROUBLESHOOTING TIPS ===")
        logger.info("1. Check that YOUTUBE_API_KEY is set in your .env file")
        logger.info("2. Verify that your YouTube API key is valid and has quota available")
        logger.info("3. Make sure you have installed all required dependencies:")
        logger.info("   pip install google-api-python-client youtube-transcript-api")
        logger.info("4. Check if the YouTube API or youtube-transcript-api is having service issues")

if __name__ == "__main__":
    main()
