"""YouTube tools for travel insights.

This module provides tools for searching and analyzing YouTube videos for travel insights.
"""

from .youtube import search_videos, get_transcript
from .youtube_insight import (
    search_travel_videos, 
    get_video_details, 
    extract_travel_insights,
    get_popular_travel_channels,
    get_destination_sentiment
)

__all__ = [
    "search_videos", 
    "get_transcript",
    "search_travel_videos",
    "get_video_details",
    "extract_travel_insights",
    "get_popular_travel_channels",
    "get_destination_sentiment"
]
