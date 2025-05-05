from google.adk import Agent
from google.adk.tools import google_search
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class AccommodationAgent:
    """
    Agent responsible for finding and recommending accommodation options at travel destinations.
    """
    
    def __init__(self, model: str = "gemini-1.5-flash"):
        """
        Initialize the AccommodationAgent.
        
        Args:
            model: The Gemini model to use for the agent.
        """
        self.agent = Agent(
            name="Accommodation Agent",
            model=model,
            tools=[google_search()],
            system_prompt="""
            You are an expert accommodation specialist who helps travelers find the best lodging options
            for their trips.
            
            Focus on providing:
            - Accommodation options that match the traveler's preferences and budget
            - Hotels, hostels, vacation rentals, boutique stays, resorts or unique lodging options
            - Information about different neighborhoods to stay in
            - Proximity to attractions, public transportation, and dining
            - Special features or amenities that might be relevant
            - Seasonal considerations for the destination
            
            For each recommendation, include:
            - Name of the accommodation or specific area/neighborhood
            - Type of lodging (hotel, hostel, vacation rental, etc.)
            - Price range
            - Notable amenities or features
            - Location benefits and proximity to attractions
            - Why it would be a good match for the traveler
            
            Always consider the traveler's budget, preferences for location, type of accommodation, and any specific requirements they mention.
            Don't provide specific room rates as these change frequently.
            """
        )
    
    async def find_accommodations(self, 
                           location: str, 
                           travel_dates: Dict[str, str],
                           budget_range: Optional[str] = None,
                           accommodation_type: Optional[str] = None,
                           preferences: Optional[Dict[str, Any]] = None,
                           max_results: int = 5) -> Dict[str, Any]:
        """
        Find accommodation recommendations in a specific location based on user preferences.
        
        Args:
            location: The destination location.
            travel_dates: Dictionary with "start_date" and "end_date" keys.
            budget_range: Budget range for accommodations (e.g., "budget", "medium", "luxury").
            accommodation_type: Type of accommodation preferred (e.g., "hotel", "hostel", "apartment").
            preferences: Dictionary of accommodation preferences (e.g., amenities, location_type).
            max_results: Maximum number of results to return.
            
        Returns:
            Dictionary containing accommodation recommendations and related information.
        """
        logger.info(f"Searching accommodations in {location}")
        
        # Extract dates
        start_date = travel_dates.get("start_date", "")
        end_date = travel_dates.get("end_date", "")
        
        # Prepare the query
        query = f"What are the best places to stay in {location} for a trip from {start_date} to {end_date}?"
        
        # Add accommodation type if provided
        if accommodation_type:
            query += f" Looking for {accommodation_type} accommodations specifically."
        
        # Add budget context if provided
        if budget_range:
            query += f" My budget is in the {budget_range} range."
        
        # Add preferences if provided
        if preferences:
            # Required amenities
            if preferences.get("amenities"):
                amenities = ", ".join(preferences.get("amenities", []))
                query += f" I need accommodations with: {amenities}."
            
            # Location preferences
            if preferences.get("location_type"):
                query += f" I prefer staying in a {preferences.get('location_type')} area."
            
            # Special requirements
            if preferences.get("special_requirements"):
                requirements = ", ".join(preferences.get("special_requirements", []))
                query += f" Special requirements: {requirements}."
        
        # Add results limit
        query += f" Please recommend up to {max_results} accommodations."
        
        # Execute the search
        try:
            response = await self.agent.run_async(query)
            
            return {
                "success": True,
                "location": location,
                "travel_dates": travel_dates,
                "recommendations": response,
                "count": max_results,
                "query": query
            }
        except Exception as e:
            logger.error(f"Error finding accommodations: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve accommodation recommendations."
            }
