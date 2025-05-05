from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class FlightSearchRequest(BaseModel):
    """Schema for flight search request"""
    departure_location: str = Field(..., description="Origin city/airport")
    destination: str = Field(..., description="Destination city/airport")
    travel_dates: Dict[str, str] = Field(..., description="Dictionary with start_date and end_date keys")
    budget_range: Optional[str] = Field(None, description="Budget range (e.g., 'budget', 'medium', 'luxury')")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Dictionary of flight preferences")

class FlightSearchResponse(BaseModel):
    """Schema for flight search response"""
    success: bool = Field(..., description="Whether the request was successful")
    departure: Optional[str] = Field(None, description="Departure location")
    destination: Optional[str] = Field(None, description="Destination location")
    travel_dates: Optional[Dict[str, str]] = Field(None, description="Travel dates searched")
    recommendations: Optional[str] = Field(None, description="Flight recommendations")
    query: Optional[str] = Field(None, description="Query used for the search")
    error: Optional[str] = Field(None, description="Error message if request failed")
    message: Optional[str] = Field(None, description="Additional message about the response")
