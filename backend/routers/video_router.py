from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any, List
import logging

from ..schemas.video_schemas import VideoSearchRequest, VideoSearchResponse
from ..agents.youtube_video_agent import YouTubeVideoAgent

router = APIRouter(prefix="/videos", tags=["videos"])
logger = logging.getLogger(__name__)

# Agent instance
video_agent = YouTubeVideoAgent()

@router.post("/search", response_model=VideoSearchResponse)
async def search_videos(request: VideoSearchRequest):
    """
    Search for travel videos about a specific location based on user preferences.
    """
    try:
        logger.info(f"Video search request for: {request.location}")
        
        result = await video_agent.find_travel_videos(
            location=request.location,
            topic=request.topic,
            max_results=request.max_results,
            include_transcripts=request.include_transcripts
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to search videos"))
        
        return result
    
    except Exception as e:
        logger.error(f"Error in video search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transcript/{video_id}", response_model=Dict[str, Any])
async def get_video_transcript(video_id: str, language_code: str = "en"):
    """
    Get the transcript of a specific YouTube video.
    """
    try:
        logger.info(f"Transcript request for video: {video_id}")
        
        result = await video_agent.get_video_transcript(
            video_id=video_id,
            language_code=language_code
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to get video transcript"))
        
        return result
    
    except Exception as e:
        logger.error(f"Error getting video transcript: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
