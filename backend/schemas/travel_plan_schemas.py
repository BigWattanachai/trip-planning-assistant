from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class TravelPlanRequest(BaseModel):
    """Schema for travel plan creation request"""
    departure_location: str = Field(..., description="Origin city/airport")
    destination: str = Field(..., description="Destination city/airport")
    travel_dates: Dict[str, str] = Field(..., description="Dictionary with start_date and end_date keys")
    budget_range: Optional[str] = Field(None, description="Budget range (e.g., 'budget', 'medium', 'luxury')")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Dictionary of various trip preferences")
    include_videos: bool = Field(True, description="Whether to include video recommendations")

class TravelPlanResponse(BaseModel):
    """Schema for travel plan response"""
    success: bool = Field(..., description="Whether the request was successful")
    departure_location: Optional[str] = Field(None, description="Origin location")
    destination: Optional[str] = Field(None, description="Destination location")
    travel_dates: Optional[Dict[str, str]] = Field(None, description="Travel dates for the trip")
    budget_range: Optional[str] = Field(None, description="Budget range for the trip")
    integrated_plan: Optional[str] = Field(None, description="Comprehensive travel plan")
    components: Optional[Dict[str, bool]] = Field(None, description="Success status of individual component searches")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw data from all agent queries")
    error: Optional[str] = Field(None, description="Error message if request failed")
    message: Optional[str] = Field(None, description="Additional message about the response")

class DestinationInsightRequest(BaseModel):
    """Schema for destination insight request"""
    destination: str = Field(..., description="Destination location to get insights about")

class DestinationInsightResponse(BaseModel):
    """Schema for destination insight response"""
    success: bool = Field(..., description="Whether the request was successful")
    destination: Optional[str] = Field(None, description="Destination location")
    insights: Optional[str] = Field(None, description="Destination insights")
    error: Optional[str] = Field(None, description="Error message if request failed")
    message: Optional[str] = Field(None, description="Additional message about the response")
