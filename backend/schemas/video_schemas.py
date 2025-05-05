from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class VideoSearchRequest(BaseModel):
    """Schema for video search request"""
    location: str = Field(..., description="Destination location to search for videos")
    topic: Optional[str] = Field(None, description="Specific topic of interest")
    max_results: int = Field(3, description="Maximum number of videos to return")
    include_transcripts: bool = Field(False, description="Whether to include video transcripts")

class VideoInfo(BaseModel):
    """Schema for video information"""
    video_id: str = Field(..., description="YouTube video ID")
    url: str = Field(..., description="Full video URL")
    embed_url: str = Field(..., description="Embeddable URL for the video")
    transcript_available: Optional[bool] = Field(None, description="Whether transcript is available")
    transcript: Optional[str] = Field(None, description="Video transcript if requested and available")

class VideoSearchResponse(BaseModel):
    """Schema for video search response"""
    success: bool = Field(..., description="Whether the request was successful")
    location: Optional[str] = Field(None, description="Location searched for videos")
    topic: Optional[str] = Field(None, description="Topic searched for videos")
    videos: Optional[List[Dict[str, Any]]] = Field(None, description="List of video information")
    analysis: Optional[str] = Field(None, description="Analysis of the videos")
    count: Optional[int] = Field(None, description="Number of videos returned")
    error: Optional[str] = Field(None, description="Error message if request failed")
    message: Optional[str] = Field(None, description="Additional message about the response")
