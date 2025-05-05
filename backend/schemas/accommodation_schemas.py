from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class AccommodationSearchRequest(BaseModel):
    """Schema for accommodation search request"""
    location: str = Field(..., description="Destination location to search for accommodations")
    travel_dates: Dict[str, str] = Field(..., description="Dictionary with start_date and end_date keys")
    budget_range: Optional[str] = Field(None, description="Budget range (e.g., 'budget', 'medium', 'luxury')")
    accommodation_type: Optional[str] = Field(None, description="Type of accommodation preferred")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Dictionary of accommodation preferences")
    max_results: int = Field(5, description="Maximum number of results to return")

class AccommodationSearchResponse(BaseModel):
    """Schema for accommodation search response"""
    success: bool = Field(..., description="Whether the request was successful")
    location: Optional[str] = Field(None, description="Location searched for accommodations")
    travel_dates: Optional[Dict[str, str]] = Field(None, description="Travel dates searched")
    recommendations: Optional[str] = Field(None, description="Accommodation recommendations")
    count: Optional[int] = Field(None, description="Number of results returned")
    query: Optional[str] = Field(None, description="Query used for the search")
    error: Optional[str] = Field(None, description="Error message if request failed")
    message: Optional[str] = Field(None, description="Additional message about the response")
