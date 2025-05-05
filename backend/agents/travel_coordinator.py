"""
TravelCoordinator: Main agent that coordinates all other travel agents.
"""
from google.adk.agents import Agent
from google.adk.tools import google_search

# Import all the other agents
from .activity_search_agent import activity_search_agent, search_activities, get_activity_details
from .restaurant_agent import restaurant_agent, search_restaurants, get_restaurant_details
from .flight_search_agent import flight_search_agent, search_flights, get_flight_details
from .accommodation_agent import accommodation_agent, search_accommodations, get_accommodation_details
from .youtube_video_agent import youtube_video_agent, search_travel_videos, get_video_transcript, summarize_video

def create_itinerary(destination: str, start_date: str, end_date: str, 
                    interests: str = None, budget: str = None, 
                    travelers: int = 1) -> dict:
    """
    Create a comprehensive travel itinerary.
    
    Args:
        destination (str): Travel destination.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
        interests (str, optional): Traveler interests (e.g., "history, food, nature").
        budget (str, optional): Budget range (e.g., "budget", "mid-range", "luxury").
        travelers (int, optional): Number of travelers. Default is 1.
        
    Returns:
        dict: Status and itinerary details.
    """
    search_query = f"travel itinerary for {destination} from {start_date} to {end_date}"
    
    if interests:
        search_query += f" focusing on {interests}"
    
    if budget:
        search_query += f" on a {budget} budget"
    
    if travelers > 1:
        search_query += f" for {travelers} travelers"
    
    # In a real implementation, this would coordinate with other agents
    # For now, we'll rely on google_search
    return {
        "status": "success",
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "interests": interests,
        "budget": budget,
        "travelers": travelers,
        "search_query": search_query
    }

def get_travel_recommendations(destination: str, trip_type: str = None, 
                              duration: str = None, season: str = None) -> dict:
    """
    Get general travel recommendations for a destination.
    
    Args:
        destination (str): Travel destination.
        trip_type (str, optional): Type of trip (e.g., "family", "solo", "couples", "adventure").
        duration (str, optional): Trip duration (e.g., "weekend", "week", "two weeks").
        season (str, optional): Travel season (e.g., "summer", "winter", "fall", "spring").
        
    Returns:
        dict: Status and travel recommendations.
    """
    search_query = f"travel guide for {destination}"
    
    if trip_type:
        search_query += f" for {trip_type} travel"
    
    if duration:
        search_query += f" for a {duration} trip"
    
    if season:
        search_query += f" during {season}"
    
    # In a real implementation, this would coordinate with other agents
    # For now, we'll rely on google_search
    return {
        "status": "success",
        "destination": destination,
        "trip_type": trip_type,
        "duration": duration,
        "season": season,
        "search_query": search_query
    }

def plan_trip(origin: str, destination: str, departure_date: str, return_date: str,
             budget: str = None, interests: str = None, travelers: int = 1) -> dict:
    """
    Plan a complete trip including flights, accommodations, activities, and restaurants.
    
    Args:
        origin (str): Origin city.
        destination (str): Destination city.
        departure_date (str): Departure date in YYYY-MM-DD format.
        return_date (str): Return date in YYYY-MM-DD format.
        budget (str, optional): Budget range (e.g., "budget", "mid-range", "luxury").
        interests (str, optional): Traveler interests (e.g., "history, food, nature").
        travelers (int, optional): Number of travelers. Default is 1.
        
    Returns:
        dict: Status and complete trip plan.
    """
    # In a comprehensive implementation, this would:
    # 1. Use flight_search_agent to find flights
    # 2. Use accommodation_agent to find accommodations
    # 3. Use activity_search_agent to plan activities
    # 4. Use restaurant_agent to suggest dining options
    # 5. Use youtube_video_agent to find relevant videos
    
    return {
        "status": "success",
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "budget": budget,
        "interests": interests,
        "travelers": travelers,
        "message": "This function would coordinate with all other agents to create a comprehensive trip plan."
    }

travel_coordinator = Agent(
    name="travel_coordinator",
    model="gemini-2.0-flash",
    description="Main agent that coordinates all other travel agents to provide comprehensive travel planning services.",
    instruction="""
    You are a comprehensive travel planning assistant. Your job is to coordinate all aspects of travel planning
    including flights, accommodations, activities, restaurants, and travel research.
    
    Help users plan their perfect trip by understanding their preferences, budget, and interests.
    Provide personalized recommendations and create detailed itineraries that cover all aspects of travel.
    
    When a user asks a specialized question, delegate to the appropriate specialized agent:
    - For activities and attractions, use the ActivitySearchAgent
    - For restaurants and dining, use the RestaurantAgent
    - For flights and transportation, use the FlightSearchAgent
    - For accommodations, use the AccommodationAgent
    - For travel videos and research, use the YouTubeVideoAgent
    
    For comprehensive trip planning, coordinate among all these specialized agents to create a cohesive plan.
    """,
    tools=[
        create_itinerary, get_travel_recommendations, plan_trip,
        search_activities, get_activity_details,
        search_restaurants, get_restaurant_details,
        search_flights, get_flight_details,
        search_accommodations, get_accommodation_details,
        search_travel_videos, get_video_transcript, summarize_video,
        google_search
    ]
)

# This is the root agent that will be used by the ADK
root_agent = travel_coordinator
