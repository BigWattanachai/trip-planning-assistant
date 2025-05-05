from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any, List
import logging

from ..schemas.activity_schemas import ActivitySearchRequest, ActivitySearchResponse
from ..agents.activity_search_agent import ActivitySearchAgent

router = APIRouter(prefix="/activities", tags=["activities"])
logger = logging.getLogger(__name__)

# Agent instance
activity_agent = ActivitySearchAgent()

@router.post("/search", response_model=ActivitySearchResponse)
async def search_activities(request: ActivitySearchRequest):
    """
    Search for activities in a specific location based on user preferences.
    """
    try:
        logger.info(f"Activity search request for: {request.location}")
        
        result = await activity_agent.search_activities(
            location=request.location,
            travel_dates=request.travel_dates,
            budget_range=request.budget_range,
            preferences=request.preferences,
            max_results=request.max_results
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to search activities"))
        
        return result
    
    except Exception as e:
        logger.error(f"Error in activity search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
