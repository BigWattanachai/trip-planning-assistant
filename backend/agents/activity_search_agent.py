"""
Activity Search Agent: An agent for finding activities in a destination with tools.
"""
import json
import requests
from typing import List, Dict, Any, Optional
from google.adk.agents import Agent

def search_activities(location: str, interests: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Search for activities and attractions in a specific location based on user interests.

    Args:
        location: The destination city or country to search for activities.
        interests: Optional list of specific interests (e.g., "hiking", "museums", "food").

    Returns:
        A dictionary containing a list of activities with their details:
        {
            "activities": [
                {
                    "name": "Activity name",
                    "type": "Type of activity (e.g., outdoor, cultural)",
                    "description": "Brief description of the activity",
                    "highlights": "What makes this activity special",
                    "practical_info": "Location, hours, cost, etc."
                },
                ...
            ]
        }
    """
    # In a real implementation, this would call an external API or database
    # For this example, we'll simulate a response with mock data

    # Simulate API call delay and processing
    sample_activities = {
        "bangkok": [
            {
                "name": "Grand Palace",
                "type": "Cultural",
                "description": "Historic complex of buildings in the heart of Bangkok",
                "highlights": "Temple of the Emerald Buddha, ornate architecture",
                "practical_info": "Open daily 8:30-15:30, 500 THB entrance fee"
            },
            {
                "name": "Chatuchak Weekend Market",
                "type": "Shopping",
                "description": "One of the world's largest weekend markets",
                "highlights": "Over 8,000 stalls selling everything imaginable",
                "practical_info": "Open weekends 9:00-18:00, free entrance"
            }
        ],
        "chiang mai": [
            {
                "name": "Doi Suthep",
                "type": "Cultural/Outdoor",
                "description": "Sacred temple on a mountain overlooking Chiang Mai",
                "highlights": "Golden pagoda, panoramic views of the city",
                "practical_info": "Open daily 6:00-18:00, 30 THB entrance fee"
            },
            {
                "name": "Elephant Nature Park",
                "type": "Wildlife/Ethical Tourism",
                "description": "Elephant rescue and rehabilitation center",
                "highlights": "Ethical elephant interactions, conservation education",
                "practical_info": "Advance booking required, 2,500 THB for day visit"
            }
        ],
        "phuket": [
            {
                "name": "Patong Beach",
                "type": "Beach/Nightlife",
                "description": "Bustling beach with vibrant nightlife",
                "highlights": "Clear waters, water sports, nearby entertainment",
                "practical_info": "Free access, best visited early morning or late afternoon"
            },
            {
                "name": "Big Buddha",
                "type": "Cultural",
                "description": "45-meter tall marble Buddha statue",
                "highlights": "Panoramic views, peaceful atmosphere",
                "practical_info": "Open daily 8:00-19:30, free entrance (donations welcome)"
            }
        ]
    }

    # Default to empty list if location not found
    location_lower = location.lower()
    activities = sample_activities.get(location_lower, [])

    # Filter by interests if provided
    if interests and activities:
        filtered_activities = []
        for activity in activities:
            # Simple matching - in a real implementation, this would be more sophisticated
            if any(interest.lower() in activity["type"].lower() or 
                   interest.lower() in activity["description"].lower() 
                   for interest in interests):
                filtered_activities.append(activity)

        # If no matches found, return all activities for the location
        activities = filtered_activities if filtered_activities else activities

    return {"activities": activities}

def get_activity_details(activity_name: str, location: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific activity or attraction.

    Args:
        activity_name: The name of the activity or attraction.
        location: The city or country where the activity is located.

    Returns:
        A dictionary containing detailed information about the activity:
        {
            "name": "Activity name",
            "location": "Specific location details",
            "description": "Detailed description",
            "opening_hours": "Operating hours",
            "entrance_fee": "Cost information in THB",
            "tips": "Visitor tips and recommendations",
            "nearby": "Nearby attractions or facilities"
        }
    """
    # In a real implementation, this would call an external API or database
    # For this example, we'll simulate a response with mock data

    # Sample detailed information for a few activities
    activity_details = {
        "grand palace": {
            "name": "Grand Palace",
            "location": "Na Phra Lan Road, Bangkok",
            "description": "The Grand Palace is a complex of buildings in Bangkok, Thailand. It served as the official residence of the Kings of Siam (and later Thailand) from 1782 to 1925. The king, his court, and his royal government were based on the grounds of the palace. The Grand Palace is divided into four main courts, separated by numerous walls and gates: the Outer Court, the Middle Court, the Inner Court, and the Temple of the Emerald Buddha.",
            "opening_hours": "Daily from 8:30 AM to 3:30 PM",
            "entrance_fee": "500 THB for foreigners, free for Thai nationals",
            "tips": "Dress modestly - shoulders and knees must be covered. Arrive early to avoid crowds and heat. Audio guides are available for 200 THB.",
            "nearby": "Wat Pho (Temple of the Reclining Buddha) is within walking distance."
        },
        "elephant nature park": {
            "name": "Elephant Nature Park",
            "location": "60 km from Chiang Mai city",
            "description": "Elephant Nature Park is an elephant rescue and rehabilitation center in Northern Thailand where you can volunteer and visit to help elephants, dogs, cats, buffaloes and many other animals. The park provides a natural environment for elephants and other rescued animals.",
            "opening_hours": "Daily visits from 9:00 AM to 5:30 PM",
            "entrance_fee": "2,500 THB for a day visit, 6,000 THB for overnight stay",
            "tips": "Book well in advance as spots fill up quickly. Wear comfortable clothes and bring sun protection. No elephant riding is offered as this is an ethical sanctuary.",
            "nearby": "Mae Taeng River for rafting activities."
        }
    }

    # Normalize input for matching
    activity_key = activity_name.lower()

    # Return details if found, otherwise return a not found message
    if activity_key in activity_details:
        return activity_details[activity_key]
    else:
        return {
            "name": activity_name,
            "location": location,
            "description": "Detailed information not available for this attraction.",
            "opening_hours": "Information not available",
            "entrance_fee": "Information not available",
            "tips": "We recommend checking official websites or local tourist information centers for the most up-to-date information.",
            "nearby": "Information not available"
        }

# Create the activity search agent with tools
activity_search_agent = Agent(
    # A unique name for the agent.
    name="activity_search_agent",
    # The Large Language Model (LLM) that agent will use.
    model="gemini-1.5-flash",
    # A short description of the agent's purpose.
    description="Agent to help find activities and attractions in a destination.",
    # Instructions to set the agent's behavior.
    instruction="""
    You are a helpful activity search assistant. Your job is to help users find interesting
    activities, attractions, and things to do in their travel destination.

    When users ask about activities in a specific location, use your tools to search for activities
    and provide detailed information. You have two main tools:

    1. search_activities: Use this to find activities in a location based on interests
    2. get_activity_details: Use this to get detailed information about a specific activity

    Always be friendly, informative, and considerate of the user's preferences.
    If the user mentions specific interests (like hiking, museums, food, etc.),
    include these when searching for activities.

    When recommending activities, include:
    - Name of the activity/attraction
    - Brief description
    - Why it's worth visiting
    - Practical information (location, best time to visit, etc.)

    If you don't know specific details about an attraction, acknowledge that and provide
    general information that would still be helpful.

    Always present information in Thai Baht (THB) instead of USD when discussing costs.
    """,
    # Add the tools to the agent
    tools=[search_activities, get_activity_details]
)
