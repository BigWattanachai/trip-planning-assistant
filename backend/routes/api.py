from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import os
import asyncio
import logging
from datetime import datetime, timedelta

from agents.agent_system import TravelAgentSystem
from services.mcp_integration import MCPIntegration
from models.schemas import (
    TripRequest, 
    TripResponse, 
    ChatMessage, 
    ChatResponse,
    DestinationInfo,
    WeatherInfo,
    CurrencyInfo
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api")

# Initialize agent system
agent_system = TravelAgentSystem()

# Initialize MCP integration
mcp_integration = MCPIntegration()

# In-memory cache for commonly requested data
cache = {}
CACHE_EXPIRY = 3600  # 1 hour in seconds

async def get_cached_data(key: str, fetch_func, *args, **kwargs):
    """Get data from cache or fetch if not available"""
    current_time = datetime.now()
    
    if key in cache and (current_time - cache[key]["timestamp"]).seconds < CACHE_EXPIRY:
        return cache[key]["data"]
    
    data = await fetch_func(*args, **kwargs)
    
    # Cache the result
    cache[key] = {
        "data": data,
        "timestamp": current_time
    }
    
    return data

@router.post("/plan-trip", response_model=TripResponse)
async def plan_trip(request: TripRequest, background_tasks: BackgroundTasks):
    """
    Plan a complete trip based on user requirements
    """
    try:
        logger.info(f"Planning trip to {request.destination} from {request.departure}")
        
        # Get weather information in background
        background_tasks.add_task(
            cache_destination_weather,
            request.destination,
            request.startDate,
            request.endDate
        )
        
        # Get currency information in background if international trip
        if request.departure != request.destination:
            background_tasks.add_task(
                cache_currency_info,
                request.departure,
                request.destination
            )
        
        # Plan trip using agent system
        result = await agent_system.plan_trip(
            departure=request.departure,
            destination=request.destination,
            start_date=request.startDate,
            end_date=request.endDate,
            budget=request.budgetRange,
            preferences=request.preferences or {}
        )
        
        # Convert to response model
        response = TripResponse(
            destination=result.get("destination"),
            departure=result.get("departure"),
            startDate=result.get("startDate"),
            endDate=result.get("endDate"),
            budget=result.get("budget"),
            activities=result.get("activities", []),
            restaurants=result.get("restaurants", []),
            flights=result.get("flights", []),
            accommodations=result.get("accommodations", []),
            videos=result.get("videos", []),
            summary=result.get("summary", ""),
            requestId=str(hash(f"{request.departure}-{request.destination}-{request.startDate}")),
            createdAt=datetime.now().isoformat()
        )
        
        return response
    except Exception as e:
        logger.error(f"Error planning trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(message: ChatMessage):
    """
    Chat with the travel agent for questions and refinements
    """
    try:
        logger.info(f"Processing chat message: {message.message[:50]}...")
        
        response = await agent_system.chat(
            message=message.message,
            session_id=message.sessionId
        )
        
        return ChatResponse(
            response=response.get("response", ""),
            sessionId=response.get("session_id", ""),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/destinations/{destination}", response_model=DestinationInfo)
async def get_destination_info(destination: str):
    """Get detailed information about a destination"""
    try:
        logger.info(f"Getting info for destination: {destination}")
        
        # Use cached data if available
        info = await get_cached_data(
            f"destination_{destination}",
            agent_system.get_destination_info,
            destination
        )
        
        return DestinationInfo(
            destination=destination,
            overview=info.get("overview", ""),
            highlights=info.get("highlights", []),
            weather=await get_destination_weather(destination),
            currency=await get_currency_info(destination),
            bestTimeToVisit=info.get("best_time_to_visit", ""),
            safetyInfo=info.get("safety_info", ""),
            localTips=info.get("local_tips", [])
        )
    except Exception as e:
        logger.error(f"Error getting destination info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "agents": agent_system.get_agent_statuses()
    }

@router.get("/weather/{destination}")
async def get_destination_weather(destination: str) -> WeatherInfo:
    """Get weather information for a destination"""
    try:
        # Calculate date range (current date + 7 days)
        today = datetime.now()
        week_later = today + timedelta(days=7)
        
        # Use cached data if available
        weather_data = await get_cached_data(
            f"weather_{destination}",
            mcp_integration.get_weather_forecast,
            destination,
            {
                "start_date": today.strftime("%Y-%m-%d"),
                "end_date": week_later.strftime("%Y-%m-%d")
            }
        )
        
        if "error" in weather_data:
            return WeatherInfo(
                destination=destination,
                currentConditions="Information not available",
                forecast=[],
                lastUpdated=datetime.now().isoformat()
            )
        
        return WeatherInfo(
            destination=destination,
            currentConditions=weather_data.get("current", {}).get("description", ""),
            temperature=weather_data.get("current", {}).get("temperature"),
            forecast=weather_data.get("forecast", []),
            lastUpdated=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error getting weather: {e}")
        return WeatherInfo(
            destination=destination,
            currentConditions="Error fetching weather data",
            forecast=[],
            lastUpdated=datetime.now().isoformat()
        )

@router.get("/currency/{origin}/{destination}")
async def get_currency_info(destination: str, origin: str = "USD") -> CurrencyInfo:
    """Get currency information for an international trip"""
    try:
        # Use cached data if available
        currency_data = await get_cached_data(
            f"currency_{origin}_{destination}",
            mcp_integration.get_exchange_rates,
            origin,
            [destination]
        )
        
        if "error" in currency_data:
            return CurrencyInfo(
                originCurrency=origin,
                destinationCurrency=destination,
                exchangeRate=None,
                lastUpdated=datetime.now().isoformat()
            )
        
        return CurrencyInfo(
            originCurrency=origin,
            destinationCurrency=destination,
            exchangeRate=currency_data.get("rates", {}).get(destination),
            lastUpdated=currency_data.get("timestamp", datetime.now().isoformat())
        )
    except Exception as e:
        logger.error(f"Error getting currency info: {e}")
        return CurrencyInfo(
            originCurrency=origin,
            destinationCurrency=destination,
            exchangeRate=None,
            lastUpdated=datetime.now().isoformat()
        )

# Background tasks
async def cache_destination_weather(destination: str, start_date: str, end_date: str):
    """Cache weather data for destination"""
    try:
        await mcp_integration.get_weather_forecast(
            destination,
            {
                "start_date": start_date,
                "end_date": end_date
            }
        )
        logger.info(f"Weather data for {destination} cached successfully")
    except Exception as e:
        logger.error(f"Error caching weather data: {e}")

async def cache_currency_info(origin: str, destination: str):
    """Cache currency exchange data"""
    try:
        await mcp_integration.get_exchange_rates(
            origin,
            [destination]
        )
        logger.info(f"Currency data for {origin} to {destination} cached successfully")
    except Exception as e:
        logger.error(f"Error caching currency data: {e}")
