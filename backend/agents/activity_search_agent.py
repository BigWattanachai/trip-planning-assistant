"""
ActivitySearchAgent: Agent for searching and recommending activities at travel destinations.
"""
from google.adk.agents import Agent
from google.adk.tools import google_search

def search_activities(location: str, preferences: str = None, budget: str = None) -> dict:
    """
    Search for activities in the specified location based on preferences and budget.
    
    Args:
        location (str): The destination location.
        preferences (str, optional): User preferences (e.g., "outdoor", "museums", "family-friendly").
        budget (str, optional): Budget range for activities (e.g., "budget", "mid-range", "luxury").
        
    Returns:
        dict: Status and activity recommendations.
    """
    search_query = f"top activities and attractions in {location}"
    
    if preferences:
        search_query += f" {preferences}"
    
    if budget:
        search_query += f" {budget} price"
    
    # In a real implementation, this would use APIs like TripAdvisor, Google Places, etc.
    # For now, we'll rely on google_search
    return {
        "status": "success",
        "location": location,
        "preferences": preferences,
        "budget": budget,
        "search_query": search_query
    }

def get_activity_details(activity_id: str, location: str) -> dict:
    """
    Get detailed information about a specific activity.
    
    Args:
        activity_id (str): Identifier for the activity.
        location (str): The destination location.
        
    Returns:
        dict: Detailed information about the activity.
    """
    # This would typically fetch data from an external API
    return {
        "status": "success",
        "activity_id": activity_id,
        "location": location,
        "search_query": f"details for {activity_id} in {location}"
    }

activity_search_agent = Agent(
    name="activity_search_agent",
    model="gemini-2.0-flash",
    description="Agent to search for and recommend activities at travel destinations.",
    instruction="""
    You are an expert travel activities advisor. Help users find the best activities and 
    attractions at their destinations based on their preferences, budget, and interests.
    Always provide practical information like estimated costs, time needed, and tips for the best experience.
    """,
    tools=[search_activities, get_activity_details, google_search]
)
