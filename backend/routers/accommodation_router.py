from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any, List
import logging

from ..schemas.accommodation_schemas import AccommodationSearchRequest, AccommodationSearchResponse
from ..agents.accommodation_agent import AccommodationAgent

router = APIRouter(prefix="/accommodations", tags=["accommodations"])
logger = logging.getLogger(__name__)

# Agent instance
accommodation_agent = AccommodationAgent()

@router.post("/search", response_model=AccommodationSearchResponse)
async def search_accommodations(request: AccommodationSearchRequest):
    """
    Search for accommodation options in a specific location based on user preferences.
    """
    try:
        logger.info(f"Accommodation search request for: {request.location}")
        
        result = await accommodation_agent.find_accommodations(
            location=request.location,
            travel_dates=request.travel_dates,
            budget_range=request.budget_range,
            accommodation_type=request.accommodation_type,
            preferences=request.preferences,
            max_results=request.max_results
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to search accommodations"))
        
        return result
    
    except Exception as e:
        logger.error(f"Error in accommodation search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
