from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any, List
import logging

from ..schemas.restaurant_schemas import RestaurantSearchRequest, RestaurantSearchResponse
from ..agents.restaurant_agent import RestaurantAgent

router = APIRouter(prefix="/restaurants", tags=["restaurants"])
logger = logging.getLogger(__name__)

# Agent instance
restaurant_agent = RestaurantAgent()

@router.post("/search", response_model=RestaurantSearchResponse)
async def search_restaurants(request: RestaurantSearchRequest):
    """
    Search for restaurants in a specific location based on user preferences.
    """
    try:
        logger.info(f"Restaurant search request for: {request.location}")
        
        result = await restaurant_agent.find_restaurants(
            location=request.location,
            cuisine_type=request.cuisine_type,
            dietary_restrictions=request.dietary_restrictions,
            price_range=request.price_range,
            max_results=request.max_results
        )
        
        if not result.get("success", False):
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to search restaurants"))
        
        return result
    
    except Exception as e:
        logger.error(f"Error in restaurant search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
