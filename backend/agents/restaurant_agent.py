"""
Restaurant Agent: An agent for finding restaurants in a destination with tools.
"""
from typing import List, Dict, Any, Optional
from google.adk.agents import Agent


def search_restaurants(location: str, cuisine_type: Optional[str] = None,
                       dietary_requirements: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Search for restaurants in a specific location based on cuisine type and dietary requirements.

    Args:
        location: The destination city or country to search for restaurants.
        cuisine_type: Optional specific cuisine type (e.g., "Thai", "Italian", "Vegetarian").
        dietary_requirements: Optional list of dietary requirements (e.g., "vegetarian", "vegan", "gluten-free").

    Returns:
        A dictionary containing a list of restaurants with their details:
        {
            "restaurants": [
                {
                    "name": "Restaurant name",
                    "cuisine": "Type of cuisine",
                    "description": "Brief description of the restaurant",
                    "signature_dishes": "Notable dishes",
                    "price_range": "Price range in THB",
                    "location": "Address or area",
                    "special_features": "Ambiance, views, etc."
                },
                ...
            ]
        }
    """
    # In a real implementation, this would call an external API or database
    # For this example, we'll simulate a response with mock data

    # Sample restaurants data
    sample_restaurants = {
        "bangkok": [
            {
                "name": "Gaggan",
                "cuisine": "Progressive Indian",
                "description": "Award-winning restaurant known for innovative Indian cuisine",
                "signature_dishes": "Yogurt explosion, charcoal prawn",
                "price_range": "4,000-6,000 THB per person",
                "location": "Sukhumvit Soi 31, Bangkok",
                "special_features": "Chef's table experience, molecular gastronomy techniques"
            },
            {
                "name": "Jay Fai",
                "cuisine": "Thai Street Food",
                "description": "Michelin-starred street food stall run by an elderly chef in goggles",
                "signature_dishes": "Crab omelette, drunken noodles",
                "price_range": "800-1,500 THB per person",
                "location": "Maha Chai Road, Bangkok",
                "special_features": "Watch the legendary chef cook with woks over charcoal"
            },
            {
                "name": "Nahm",
                "cuisine": "Traditional Thai",
                "description": "Sophisticated Thai restaurant focusing on ancient recipes",
                "signature_dishes": "Blue swimmer crab curry, mango sticky rice",
                "price_range": "2,500-3,500 THB per person",
                "location": "COMO Metropolitan Bangkok",
                "special_features": "Elegant dining room, extensive wine list"
            }
        ],
        "chiang mai": [
            {
                "name": "Huen Phen",
                "cuisine": "Northern Thai",
                "description": "Authentic Northern Thai cuisine in a traditional setting",
                "signature_dishes": "Khao soi, nam prik ong",
                "price_range": "200-400 THB per person",
                "location": "Ratchamanka Road, Old City, Chiang Mai",
                "special_features": "Traditional Lanna decor, local atmosphere"
            },
            {
                "name": "David's Kitchen",
                "cuisine": "French-Thai Fusion",
                "description": "Upscale dining with personalized service",
                "signature_dishes": "Duck confit, rack of lamb",
                "price_range": "1,500-2,500 THB per person",
                "location": "Bumrungburi Road, Chiang Mai",
                "special_features": "The owner personally greets guests, elegant atmosphere"
            }
        ],
        "phuket": [
            {
                "name": "Blue Elephant",
                "cuisine": "Royal Thai Cuisine",
                "description": "Housed in a historic mansion serving royal Thai recipes",
                "signature_dishes": "Massaman curry, pomelo salad",
                "price_range": "1,500-2,500 THB per person",
                "location": "Krabi Road, Phuket Town",
                "special_features": "Cooking classes available, colonial architecture"
            },
            {
                "name": "Baan Rim Pa",
                "cuisine": "Royal Thai Cuisine",
                "description": "Cliffside restaurant with panoramic views of Patong Bay",
                "signature_dishes": "Goong sarong (prawns wrapped in vermicelli), panang curry",
                "price_range": "1,800-3,000 THB per person",
                "location": "Kalim Beach, Patong, Phuket",
                "special_features": "Piano bar, sunset views over the Andaman Sea"
            }
        ]
    }

    # Default to empty list if location not found
    location_lower = location.lower()
    restaurants = sample_restaurants.get(location_lower, [])

    # Filter by cuisine type if provided
    if cuisine_type and restaurants:
        cuisine_type_lower = cuisine_type.lower()
        filtered_by_cuisine = [
            restaurant for restaurant in restaurants
            if cuisine_type_lower in restaurant["cuisine"].lower()
        ]
        # Only apply filter if matches found
        if filtered_by_cuisine:
            restaurants = filtered_by_cuisine

    # Filter by dietary requirements if provided
    if dietary_requirements and restaurants:
        # This is a simplified implementation
        # In a real system, you would have more detailed dietary information
        dietary_friendly_restaurants = []
        for restaurant in restaurants:
            # Check if any dietary requirement is mentioned in the description or special features
            if any(req.lower() in restaurant["description"].lower() or
                   req.lower() in restaurant["special_features"].lower() or
                   req.lower() in restaurant["cuisine"].lower()
                   for req in dietary_requirements):
                dietary_friendly_restaurants.append(restaurant)

        # Only apply filter if matches found
        if dietary_friendly_restaurants:
            restaurants = dietary_friendly_restaurants

    return {"restaurants": restaurants}


def get_restaurant_details(restaurant_name: str, location: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific restaurant.

    Args:
        restaurant_name: The name of the restaurant.
        location: The city or country where the restaurant is located.

    Returns:
        A dictionary containing detailed information about the restaurant:
        {
            "name": "Restaurant name",
            "address": "Full address",
            "cuisine": "Type of cuisine",
            "description": "Detailed description",
            "menu_highlights": "Popular dishes",
            "price_range": "Cost information in THB",
            "opening_hours": "Operating hours",
            "reservation_info": "How to make reservations",
            "reviews": "Summary of reviews"
        }
    """
    # In a real implementation, this would call an external API or database
    # For this example, we'll simulate a response with mock data

    # Sample detailed information for a few restaurants
    restaurant_details = {
        "gaggan": {
            "name": "Gaggan",
            "address": "68/1 Soi Langsuan, Ploenchit Road, Lumpini, Bangkok 10330",
            "cuisine": "Progressive Indian",
            "description": "Gaggan is a progressive Indian restaurant that has consistently ranked among Asia's best restaurants. Chef Gaggan Anand creates innovative dishes that challenge traditional notions of Indian cuisine, using molecular gastronomy techniques to transform familiar flavors into surprising new forms.",
            "menu_highlights": "The restaurant is famous for its tasting menu, which includes the yogurt explosion, charcoal prawn, and Lick It Up (a dish you literally lick from the plate).",
            "price_range": "4,000-6,000 THB per person for the tasting menu",
            "opening_hours": "Tuesday to Sunday, 6:00 PM to 11:00 PM. Closed on Mondays.",
            "reservation_info": "Reservations required at least 2 months in advance through their website or by phone.",
            "reviews": "Multiple-time winner of Asia's 50 Best Restaurants. Known for theatrical presentation and boundary-pushing cuisine."
        },
        "jay fai": {
            "name": "Jay Fai",
            "address": "327 Maha Chai Road, Samran Rat, Phra Nakhon, Bangkok 10200",
            "cuisine": "Thai Street Food",
            "description": "Jay Fai is a street food stall that gained international fame after receiving a Michelin star. The restaurant is run by Supinya Junsuta, an elderly chef known for her signature goggles that she wears while cooking over hot charcoal fires. Despite its humble appearance, Jay Fai serves some of the most sought-after seafood dishes in Bangkok.",
            "menu_highlights": "Crab omelette (kai jeaw poo), drunken noodles (pad kee mao), and tom yum soup with seafood.",
            "price_range": "800-1,500 THB per person",
            "opening_hours": "Tuesday to Saturday, 2:00 PM to 12:00 AM. Closed on Sundays and Mondays.",
            "reservation_info": "No reservations accepted. Expect to wait in line, sometimes for hours.",
            "reviews": "Michelin-starred street food. Expensive by street food standards but justified by the quality and portion sizes."
        }
    }

    # Normalize input for matching
    restaurant_key = restaurant_name.lower()

    # Return details if found, otherwise return a not found message
    if restaurant_key in restaurant_details:
        return restaurant_details[restaurant_key]
    else:
        return {
            "name": restaurant_name,
            "address": f"Location: {location}",
            "cuisine": "Information not available",
            "description": "Detailed information not available for this restaurant.",
            "menu_highlights": "Information not available",
            "price_range": "Information not available",
            "opening_hours": "Information not available",
            "reservation_info": "We recommend checking the restaurant's official website or calling directly for reservation information.",
            "reviews": "Information not available"
        }


# Create the restaurant agent with tools
restaurant_agent = Agent(
    # A unique name for the agent.
    name="restaurant_agent",
    # The Large Language Model (LLM) that agent will use.
    model="gemini-1.5-flash",
    # A short description of the agent's purpose.
    description="Agent to help find restaurants and food experiences in a destination.",
    # Instructions to set the agent's behavior.
    instruction="""
    You are a helpful restaurant and food recommendation assistant. Your job is to help users
    find great places to eat and drink in their travel destination.

    When users ask about food in a specific location, use your tools to search for restaurants
    and provide detailed information. You have two main tools:

    1. search_restaurants: Use this to find restaurants in a location based on cuisine type and dietary requirements
    2. get_restaurant_details: Use this to get detailed information about a specific restaurant

    Always be friendly, informative, and considerate of the user's preferences.
    If the user mentions specific dietary requirements or cuisine preferences,
    include these when searching for restaurants.

    When recommending restaurants, include:
    - Name of the restaurant
    - Type of cuisine
    - Signature dishes
    - Price range (in Thai Baht)
    - Location
    - Any special features (views, ambiance, etc.)

    If you don't know specific details about a restaurant, acknowledge that and provide
    general information about the type of food available in that area.

    Always present prices in Thai Baht (THB) instead of USD.
    """,
    # Add the tools to the agent
    tools=[search_restaurants, get_restaurant_details]
)
