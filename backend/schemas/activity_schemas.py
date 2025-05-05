from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class ActivitySearchRequest(BaseModel):
    """Schema for activity search request"""
    location: str = Field(..., description="Destination location to search for activities")
    travel_dates: Optional[Dict[str, str]] = Field(None, description="Dictionary containing start_date and end_date")
    budget_range: Optional[str] = Field(None, description="Budget range (e.g., 'budget', 'medium', 'luxury')")
    preferences: Optional[str] = Field(None, description="Activity preferences")
    max_results: int = Field(5, description="Maximum number of results to return")

class ActivitySearchResponse(BaseModel):
    """Schema for activity search response"""
    success: bool = Field(..., description="Whether the request was successful")
    location: Optional[str] = Field(None, description="Location searched for activities")
    recommendations: Optional[str] = Field(None, description="Activity recommendations")
    count: Optional[int] = Field(None, description="Number of results returned")
    query: Optional[str] = Field(None, description="Query used for the search")
    error: Optional[str] = Field(None, description="Error message if request failed")
    message: Optional[str] = Field(None, description="Additional message about the response")
