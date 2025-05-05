"""
RestaurantAgent: Agent for finding and recommending restaurants at travel destinations.
"""
from google.adk.agents import Agent
from google.adk.tools import google_search

def search_restaurants(location: str, cuisine: str = None, 
                      budget: str = None, dietary_restrictions: str = None) -> dict:
    """
    Search for restaurants in the specified location based on cuisine, budget, and dietary restrictions.
    
    Args:
        location (str): The destination location.
        cuisine (str, optional): Type of cuisine (e.g., "Italian", "Japanese", "Local").
        budget (str, optional): Budget range (e.g., "budget", "mid-range", "fine dining").
        dietary_restrictions (str, optional): Dietary restrictions (e.g., "vegetarian", "gluten-free").
        
    Returns:
        dict: Status and restaurant recommendations.
    """
    search_query = f"restaurants in {location}"
    
    if cuisine:
        search_query += f" {cuisine} cuisine"
    
    if budget:
        search_query += f" {budget} price"
        
    if dietary_restrictions:
        search_query += f" {dietary_restrictions} options"
    
    # In a real implementation, this would use APIs like Google Places, Yelp, etc.
    # For now, we'll rely on google_search
    return {
        "status": "success",
        "location": location,
        "cuisine": cuisine,
        "budget": budget,
        "dietary_restrictions": dietary_restrictions,
        "search_query": search_query
    }

def get_restaurant_details(restaurant_id: str, location: str) -> dict:
    """
    Get detailed information about a specific restaurant.
    
    Args:
        restaurant_id (str): Identifier for the restaurant.
        location (str): The destination location.
        
    Returns:
        dict: Detailed information about the restaurant.
    """
    # This would typically fetch data from an external API
    return {
        "status": "success",
        "restaurant_id": restaurant_id,
        "location": location,
        "search_query": f"details for {restaurant_id} in {location}"
    }

restaurant_agent = Agent(
    name="restaurant_agent",
    model="gemini-2.0-flash",
    description="Agent to find and recommend restaurants at travel destinations.",
    instruction="""
    You are an expert restaurant advisor. Help users find the best dining options at their 
    destinations based on their cuisine preferences, budget, and dietary restrictions.
    Always provide practical information like price range, signature dishes, and tips for the best dining experience.
    """,
    tools=[search_restaurants, get_restaurant_details, google_search]
)
