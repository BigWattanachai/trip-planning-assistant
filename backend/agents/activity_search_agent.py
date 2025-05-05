from google.adk import Agent
from google.adk.tools import google_search
from typing import Dict, Any, Optional
import os
import logging

logger = logging.getLogger(__name__)

class ActivitySearchAgent:
    """
    Agent responsible for searching and recommending activities at travel destinations.
    """
    
    def __init__(self, model: str = "gemini-1.5-flash"):
        """
        Initialize the ActivitySearchAgent.
        
        Args:
            model: The Gemini model to use for the agent.
        """
        self.agent = Agent(
            name="Activity Search Agent",
            model=model,
            tools=[google_search()],
            system_prompt="""
            You are an expert travel activity researcher specialized in finding interesting and 
            relevant activities, attractions, and things to do at travel destinations.
            
            Focus on providing:
            - Top attractions and landmarks
            - Cultural experiences (museums, historical sites, local customs)
            - Outdoor activities (hiking, beaches, parks)
            - Entertainment options (shows, events)
            - Unique or offbeat experiences that travelers might miss
            
            For each recommendation, include:
            - Name of the activity/attraction
            - Brief description
            - Why it's worth visiting
            - Estimated time needed to visit
            - Best time to visit if relevant
            - Approximate cost if available
            
            Always consider the traveler's preferences, budget range, and travel dates in your recommendations.
            """
        )
    
    async def search_activities(self, 
                          location: str, 
                          travel_dates: Optional[Dict[str, str]] = None,
                          budget_range: Optional[str] = None,
                          preferences: Optional[str] = None,
                          max_results: int = 5) -> Dict[str, Any]:
        """
        Search for activities in a specific location based on user preferences.
        
        Args:
            location: The destination location.
            travel_dates: Dictionary with start_date and end_date (optional).
            budget_range: Budget range for activities (e.g., "budget", "medium", "luxury").
            preferences: User preferences for activities (optional).
            max_results: Maximum number of results to return.
            
        Returns:
            Dictionary containing activity recommendations and related information.
        """
        logger.info(f"Searching activities for {location}")
        
        # Prepare the query
        query = f"What are the best activities and attractions to do in {location}?"
        
        # Add date context if provided
        if travel_dates:
            start_date = travel_dates.get("start_date")
            end_date = travel_dates.get("end_date")
            if start_date and end_date:
                query += f" for a trip from {start_date} to {end_date}"
        
        # Add budget context if provided
        if budget_range:
            query += f" with a {budget_range} budget"
        
        # Add preferences if provided
        if preferences:
            query += f". I'm interested in {preferences}"
            
        # Add results limit
        query += f". Please recommend up to {max_results} activities."
        
        # Execute the search
        try:
            response = await self.agent.run_async(query)
            
            return {
                "success": True,
                "location": location,
                "recommendations": response,
                "count": max_results,
                "query": query
            }
        except Exception as e:
            logger.error(f"Error searching activities: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve activity recommendations."
            }
