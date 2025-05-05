from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional, Dict, Any, List
import logging
import asyncio

from ..schemas.travel_plan_schemas import TravelPlanRequest, TravelPlanResponse, DestinationInsightRequest, DestinationInsightResponse
from ..agents.travel_coordinator import TravelCoordinator

router = APIRouter(prefix="/travel-plans", tags=["travel-plans"])
logger = logging.getLogger(__name__)

# Agent instance
coordinator = TravelCoordinator()

@router.post("/create", response_model=TravelPlanResponse)
async def create_travel_plan(request: TravelPlanRequest):
    """
    Create a comprehensive travel plan based on user preferences.
    """
    try:
        logger.info(f"Travel plan request for trip to {request.destination}")
        
        result = await coordinator.create_travel_plan(
            departure_location=request.departure_location,
            destination=request.destination,
            travel_dates=request.travel_dates,
            budget_range=request.budget_range,
            preferences=request.preferences,
            include_videos=request.include_videos
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to create travel plan"))
        
        return result
    
    except Exception as e:
        logger.error(f"Error creating travel plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/destination-insights", response_model=DestinationInsightResponse)
async def get_destination_insights(request: DestinationInsightRequest):
    """
    Get insights about a destination to help with initial planning.
    """
    try:
        logger.info(f"Destination insights request for: {request.destination}")
        
        result = await coordinator.get_destination_insight(
            destination=request.destination
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to get destination insights"))
        
        return result
    
    except Exception as e:
        logger.error(f"Error getting destination insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
