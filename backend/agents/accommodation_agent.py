"""
AccommodationAgent: Agent for finding and recommending accommodations.
"""
from google.adk.agents import Agent
from google.adk.tools import google_search

def search_accommodations(location: str, check_in_date: str, check_out_date: str,
                         guests: int = 2, room_type: str = None, 
                         amenities: str = None, budget: str = None) -> dict:
    """
    Search for accommodations based on the specified parameters.
    
    Args:
        location (str): Destination location.
        check_in_date (str): Check-in date in YYYY-MM-DD format.
        check_out_date (str): Check-out date in YYYY-MM-DD format.
        guests (int, optional): Number of guests. Default is 2.
        room_type (str, optional): Type of room (e.g., "standard", "suite", "apartment").
        amenities (str, optional): Desired amenities (e.g., "pool", "wifi", "breakfast").
        budget (str, optional): Budget range (e.g., "budget", "mid-range", "luxury").
        
    Returns:
        dict: Status and accommodation options.
    """
    search_query = f"accommodations in {location} from {check_in_date} to {check_out_date} for {guests} guests"
    
    if room_type:
        search_query += f" {room_type} room"
    
    if amenities:
        search_query += f" with {amenities}"
    
    if budget:
        search_query += f" {budget} price"
    
    # In a real implementation, this would use accommodation APIs like Booking.com, Expedia, etc.
    # For now, we'll rely on google_search
    return {
        "status": "success",
        "location": location,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "guests": guests,
        "room_type": room_type,
        "amenities": amenities,
        "budget": budget,
        "search_query": search_query
    }

def get_accommodation_details(accommodation_id: str) -> dict:
    """
    Get detailed information about a specific accommodation.
    
    Args:
        accommodation_id (str): Identifier for the accommodation.
        
    Returns:
        dict: Detailed information about the accommodation.
    """
    # This would typically fetch data from an external API
    return {
        "status": "success",
        "accommodation_id": accommodation_id,
        "search_query": f"details for accommodation {accommodation_id}"
    }

accommodation_agent = Agent(
    name="accommodation_agent",
    model="gemini-2.0-flash",
    description="Agent to find and recommend accommodations.",
    instruction="""
    You are an expert accommodation advisor. Help users find the best places to stay based on their 
    travel criteria, preferences, and budget.
    Consider factors like location, amenities, room types, and guest reviews.
    Always provide practical information like price range, nearby attractions, and tips for the best stay.
    """,
    tools=[search_accommodations, get_accommodation_details, google_search]
)
