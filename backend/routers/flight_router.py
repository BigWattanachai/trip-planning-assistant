from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any, List
import logging

from ..schemas.flight_schemas import FlightSearchRequest, FlightSearchResponse
from ..agents.flight_search_agent import FlightSearchAgent

router = APIRouter(prefix="/flights", tags=["flights"])
logger = logging.getLogger(__name__)

# Agent instance
flight_agent = FlightSearchAgent()

@router.post("/search", response_model=FlightSearchResponse)
async def search_flights(request: FlightSearchRequest):
    """
    Search for flight options between departure and destination locations.
    """
    try:
        logger.info(f"Flight search request from {request.departure_location} to {request.destination}")
        
        result = await flight_agent.search_flights(
            departure_location=request.departure_location,
            destination=request.destination,
            travel_dates=request.travel_dates,
            budget_range=request.budget_range,
            preferences=request.preferences
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to search flights"))
        
        return result
    
    except Exception as e:
        logger.error(f"Error in flight search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
