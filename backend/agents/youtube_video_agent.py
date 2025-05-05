"""
YouTubeVideoAgent: Agent for finding and recommending travel-related YouTube videos.
"""
from google.adk.agents import Agent
from google.adk.tools import google_search
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

def search_travel_videos(destination: str, content_type: str = None) -> dict:
    """
    Search for travel-related YouTube videos for a specific destination.
    
    Args:
        destination (str): The travel destination.
        content_type (str, optional): Type of content (e.g., "guide", "vlog", "tips", "food tour").
        
    Returns:
        dict: Status and video recommendations.
    """
    search_query = f"travel {destination} youtube"
    
    if content_type:
        search_query += f" {content_type}"
    
    # In a real implementation, this would use the YouTube API
    # For now, we'll rely on google_search
    return {
        "status": "success",
        "destination": destination,
        "content_type": content_type,
        "search_query": search_query
    }

def get_video_transcript(video_id: str) -> dict:
    """
    Get the transcript of a YouTube video.
    
    Args:
        video_id (str): YouTube video ID.
        
    Returns:
        dict: Status and video transcript.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return {
            "status": "success",
            "video_id": video_id,
            "transcript": transcript
        }
    except TranscriptsDisabled:
        return {
            "status": "error",
            "error_message": "Transcripts are disabled for this video."
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }

def summarize_video(video_id: str) -> dict:
    """
    Summarize the content of a YouTube video.
    
    Args:
        video_id (str): YouTube video ID.
        
    Returns:
        dict: Status and video summary.
    """
    # First, try to get the transcript
    transcript_result = get_video_transcript(video_id)
    
    if transcript_result["status"] == "error":
        return transcript_result
    
    # In a real implementation, we would use the LLM to summarize the transcript
    # Here, we'll just return the transcript as is
    return {
        "status": "success",
        "video_id": video_id,
        "transcript": transcript_result["transcript"],
        "search_query": f"summary of YouTube video {video_id}"
    }

youtube_video_agent = Agent(
    name="youtube_video_agent",
    model="gemini-2.0-flash",
    description="Agent to find and recommend travel-related YouTube videos.",
    instruction="""
    You are an expert travel video curator. Help users find the best travel videos for their 
    destinations, providing valuable visual content to enhance their travel planning.
    Focus on high-quality, informative, and visually appealing content from reputable travel creators.
    Always provide context about what users can expect to learn from each video.
    """,
    tools=[search_travel_videos, get_video_transcript, summarize_video, google_search]
)
