"""
FlightSearchAgent: Agent for searching and recommending flights.
"""
from google.adk.agents import Agent
from google.adk.tools import google_search

def search_flights(origin: str, destination: str, departure_date: str, 
                  return_date: str = None, passengers: int = 1, 
                  cabin_class: str = "economy") -> dict:
    """
    Search for flights based on the specified parameters.
    
    Args:
        origin (str): Origin city or airport code.
        destination (str): Destination city or airport code.
        departure_date (str): Departure date in YYYY-MM-DD format.
        return_date (str, optional): Return date in YYYY-MM-DD format for round trips.
        passengers (int, optional): Number of passengers. Default is 1.
        cabin_class (str, optional): Cabin class (economy, premium_economy, business, first). Default is economy.
        
    Returns:
        dict: Status and flight options.
    """
    trip_type = "one-way" if not return_date else "round-trip"
    
    search_query = f"flights from {origin} to {destination} on {departure_date}"
    
    if return_date:
        search_query += f" returning {return_date}"
    
    search_query += f" {passengers} passenger(s) {cabin_class} class"
    
    # In a real implementation, this would use flight APIs like SkyScanner, Kiwi, etc.
    # For now, we'll rely on google_search
    return {
        "status": "success",
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "passengers": passengers,
        "cabin_class": cabin_class,
        "trip_type": trip_type,
        "search_query": search_query
    }

def get_flight_details(flight_id: str) -> dict:
    """
    Get detailed information about a specific flight.
    
    Args:
        flight_id (str): Identifier for the flight.
        
    Returns:
        dict: Detailed information about the flight.
    """
    # This would typically fetch data from an external API
    return {
        "status": "success",
        "flight_id": flight_id,
        "search_query": f"details for flight {flight_id}"
    }

flight_search_agent = Agent(
    name="flight_search_agent",
    model="gemini-2.0-flash",
    description="Agent to search for and recommend flights.",
    instruction="""
    You are an expert flight advisor. Help users find the best flight options based on their travel criteria.
    Consider factors like price, duration, number of stops, and airline preferences.
    Always provide practical information like baggage allowance, in-flight amenities, and tips for the best travel experience.
    """,
    tools=[search_flights, get_flight_details, google_search]
)
