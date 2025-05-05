from google.adk import Agent
from google.adk.tools import google_search
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class RestaurantAgent:
    """
    Agent responsible for finding and recommending restaurants and dining options 
    at travel destinations.
    """
    
    def __init__(self, model: str = "gemini-1.5-flash"):
        """
        Initialize the RestaurantAgent.
        
        Args:
            model: The Gemini model to use for the agent.
        """
        self.agent = Agent(
            name="Restaurant Agent",
            model=model,
            tools=[google_search()],
            system_prompt="""
            You are an expert food and restaurant researcher specialized in finding the best dining 
            options at travel destinations.
            
            Focus on providing:
            - Local cuisine and specialties that shouldn't be missed
            - Restaurants with authentic local food
            - Popular dining establishments with great reviews
            - Options for different price ranges (budget to fine dining)
            - Dietary accommodations (vegetarian, vegan, gluten-free, etc.)
            - Unique culinary experiences (food tours, cooking classes, etc.)
            
            For each recommendation, include:
            - Name of the restaurant/dining option
            - Type of cuisine
            - Price range ($ to $$$$$)
            - Signature dishes or must-try items
            - Location details
            - Notable features (view, ambiance, historical significance)
            - Reservation requirements if relevant
            
            Always consider the traveler's dietary restrictions, cuisine preferences, and budget in your recommendations.
            """
        )
    
    async def find_restaurants(self, 
                        location: str, 
                        cuisine_type: Optional[str] = None,
                        dietary_restrictions: Optional[List[str]] = None,
                        price_range: Optional[str] = None,
                        max_results: int = 5) -> Dict[str, Any]:
        """
        Find restaurant recommendations in a specific location based on user preferences.
        
        Args:
            location: The destination location.
            cuisine_type: Type of cuisine preferred (optional).
            dietary_restrictions: List of dietary restrictions (optional).
            price_range: Budget range for dining (e.g., "budget", "medium", "luxury").
            max_results: Maximum number of results to return.
            
        Returns:
            Dictionary containing restaurant recommendations and related information.
        """
        logger.info(f"Searching restaurants in {location}")
        
        # Prepare the query
        query = f"What are the best restaurants and dining options in {location}?"
        
        # Add cuisine preferences if provided
        if cuisine_type:
            query += f" for {cuisine_type} cuisine"
        
        # Add dietary restrictions if provided
        if dietary_restrictions and len(dietary_restrictions) > 0:
            restrictions = ", ".join(dietary_restrictions)
            query += f" that accommodate {restrictions} dietary needs"
        
        # Add price range if provided
        if price_range:
            query += f" in the {price_range} price range"
            
        # Add results limit
        query += f". Please recommend up to {max_results} dining options."
        
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
            logger.error(f"Error finding restaurants: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve restaurant recommendations."
            }
