from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class RestaurantSearchRequest(BaseModel):
    """Schema for restaurant search request"""
    location: str = Field(..., description="Destination location to search for restaurants")
    cuisine_type: Optional[str] = Field(None, description="Type of cuisine preferred")
    dietary_restrictions: Optional[List[str]] = Field(None, description="List of dietary restrictions")
    price_range: Optional[str] = Field(None, description="Price range (e.g., 'budget', 'medium', 'luxury')")
    max_results: int = Field(5, description="Maximum number of results to return")

class RestaurantSearchResponse(BaseModel):
    """Schema for restaurant search response"""
    success: bool = Field(..., description="Whether the request was successful")
    location: Optional[str] = Field(None, description="Location searched for restaurants")
    recommendations: Optional[str] = Field(None, description="Restaurant recommendations")
    count: Optional[int] = Field(None, description="Number of results returned")
    query: Optional[str] = Field(None, description="Query used for the search")
    error: Optional[str] = Field(None, description="Error message if request failed")
    message: Optional[str] = Field(None, description="Additional message about the response")
