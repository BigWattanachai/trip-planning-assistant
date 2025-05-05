from google.adk import Agent
from google.adk.tools import google_search
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FlightSearchAgent:
    """
    Agent responsible for searching and recommending flight options for travel.
    """
    
    def __init__(self, model: str = "gemini-1.5-flash"):
        """
        Initialize the FlightSearchAgent.
        
        Args:
            model: The Gemini model to use for the agent.
        """
        self.agent = Agent(
            name="Flight Search Agent",
            model=model,
            tools=[google_search()],
            system_prompt="""
            You are an expert flight search specialist who helps travelers find the best flight options
            for their trips.
            
            Focus on providing:
            - Best flight options based on price, duration, and convenience
            - Direct flights when available, and good connecting options when necessary
            - Airlines that service the requested routes
            - Typical price ranges for the requested routes
            - Optimal travel times and days for better deals
            - Important considerations for specific routes (visa requirements, layover options)
            - Baggage allowance information for recommended airlines
            
            For each recommendation, include:
            - Suggested airlines
            - Approximate price range
            - Typical flight duration
            - Direct vs connecting flight options
            - Best booking strategy (how far in advance to book)
            - Tips for finding deals on this route
            
            Always consider the traveler's preferences for dates, budget, and any airline preferences in your recommendations.
            Do not provide specific flight numbers or exact prices, as these change frequently.
            """
        )
    
    async def search_flights(self, 
                      departure_location: str,
                      destination: str,
                      travel_dates: Dict[str, str],
                      budget_range: Optional[str] = None,
                      preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search for flight options between departure and destination locations.
        
        Args:
            departure_location: The origin city/airport.
            destination: The destination city/airport.
            travel_dates: Dictionary with "start_date" and "end_date" keys.
            budget_range: Budget range for flights (e.g., "budget", "medium", "luxury").
            preferences: Dictionary of flight preferences (e.g., direct_only, preferred_airlines).
            
        Returns:
            Dictionary containing flight recommendations and related information.
        """
        logger.info(f"Searching flights from {departure_location} to {destination}")
        
        # Validate dates
        try:
            start_date = travel_dates.get("start_date", "")
            end_date = travel_dates.get("end_date", "")
        except Exception as e:
            logger.error(f"Invalid date format: {str(e)}")
            return {
                "success": False,
                "error": "Invalid date format",
                "message": "Please provide valid travel dates."
            }
        
        # Prepare the query
        query = f"What are the best flight options from {departure_location} to {destination} for travel between {start_date} and {end_date}?"
        
        # Add budget context if provided
        if budget_range:
            query += f" with a {budget_range} budget"
        
        # Add preferences if provided
        if preferences:
            # Direct flights preference
            if preferences.get("direct_only"):
                query += ". I prefer direct flights only"
            
            # Airline preferences
            if preferences.get("preferred_airlines"):
                airlines = ", ".join(preferences.get("preferred_airlines", []))
                query += f". I prefer flying with {airlines}"
            
            # Cabin class preference
            if preferences.get("cabin_class"):
                query += f". I prefer flying {preferences.get('cabin_class')} class"
        
        # Execute the search
        try:
            response = await self.agent.run_async(query)
            
            return {
                "success": True,
                "departure": departure_location,
                "destination": destination,
                "travel_dates": travel_dates,
                "recommendations": response,
                "query": query
            }
        except Exception as e:
            logger.error(f"Error searching flights: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve flight recommendations."
            }
