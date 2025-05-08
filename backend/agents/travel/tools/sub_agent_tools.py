"""
Sub-agent tools for the travel agent to call specialized agents.
"""
from typing import Dict, Any
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Part, Content

# Import the specialized agents
from backend.agents.activity.activity_search_agent import activity_search_agent
from backend.agents.restaurant.restaurant_agent import restaurant_agent
from backend.agents.accommodation.accommodation_agent import accommodation_agent
from backend.agents.transportation.transportation_agent import transportation_agent

# Create session services and runners for the specialized agents
activity_session_service = InMemorySessionService()
activity_runner = Runner(
    agent=activity_search_agent, 
    app_name="Travel Planning Assistant", 
    session_service=activity_session_service
)
activity_session_service.create_session(
    app_name="Travel Planning Assistant", 
    user_id="user_123", 
    session_id="activity_session"
)

restaurant_session_service = InMemorySessionService()
restaurant_runner = Runner(
    agent=restaurant_agent, 
    app_name="Travel Planning Assistant", 
    session_service=restaurant_session_service
)
restaurant_session_service.create_session(
    app_name="Travel Planning Assistant", 
    user_id="user_123", 
    session_id="restaurant_session"
)

accommodation_session_service = InMemorySessionService()
accommodation_runner = Runner(
    agent=accommodation_agent, 
    app_name="Travel Planning Assistant", 
    session_service=accommodation_session_service
)
accommodation_session_service.create_session(
    app_name="Travel Planning Assistant", 
    user_id="user_123", 
    session_id="accommodation_session"
)

transportation_session_service = InMemorySessionService()
transportation_runner = Runner(
    agent=transportation_agent, 
    app_name="Travel Planning Assistant", 
    session_service=transportation_session_service
)
transportation_session_service.create_session(
    app_name="Travel Planning Assistant", 
    user_id="user_123", 
    session_id="transportation_session"
)

def call_activity_agent(query: str, context: str = "") -> Dict[str, Any]:
    """
    Call the activity agent to get information about activities and attractions.

    Args:
        query: The user's query about activities or attractions.
        context: Additional context information that might be helpful for the activity agent.

    Returns:
        A dictionary containing the activity agent's response.
    """
    # Combine the query and context
    enhanced_query = query
    if context:
        enhanced_query = f"{context}\n\n{query}"

    # Create content object for the agent
    content = Content(role="user", parts=[Part(text=enhanced_query)])

    # Call the activity agent
    response = activity_runner.run(
        user_id="user_123", 
        session_id="activity_session", 
        new_message=content
    )

    # Extract the response text
    response_text = ""
    if response and hasattr(response, "content") and hasattr(response.content, "parts") and len(response.content.parts) > 0:
        response_text = response.content.parts[0].text

    return {"response": response_text}

def call_restaurant_agent(query: str, context: str = "") -> Dict[str, Any]:
    """
    Call the restaurant agent to get information about restaurants and food.

    Args:
        query: The user's query about restaurants or food.
        context: Additional context information that might be helpful for the restaurant agent.

    Returns:
        A dictionary containing the restaurant agent's response.
    """
    # Combine the query and context
    enhanced_query = query
    if context:
        enhanced_query = f"{context}\n\n{query}"

    # Create content object for the agent
    content = Content(role="user", parts=[Part(text=enhanced_query)])

    # Call the restaurant agent
    response = restaurant_runner.run(
        user_id="user_123", 
        session_id="restaurant_session", 
        new_message=content
    )

    # Extract the response text
    response_text = ""
    if response and hasattr(response, "content") and hasattr(response.content, "parts") and len(response.content.parts) > 0:
        response_text = response.content.parts[0].text

    return {"response": response_text}

def call_accommodation_agent(query: str, context: str = "") -> Dict[str, Any]:
    """
    Call the accommodation agent to get information about hotels and accommodations.

    Args:
        query: The user's query about accommodations.
        context: Additional context information that might be helpful for the accommodation agent.

    Returns:
        A dictionary containing the accommodation agent's response.
    """
    # Combine the query and context
    enhanced_query = query
    if context:
        enhanced_query = f"{context}\n\n{query}"

    # Create content object for the agent
    content = Content(role="user", parts=[Part(text=enhanced_query)])

    # Call the accommodation agent
    response = accommodation_runner.run(
        user_id="user_123", 
        session_id="accommodation_session", 
        new_message=content
    )

    # Extract the response text
    response_text = ""
    if response and hasattr(response, "content") and hasattr(response.content, "parts") and len(response.content.parts) > 0:
        response_text = response.content.parts[0].text

    return {"response": response_text}

def call_transportation_agent(query: str, context: str = "") -> Dict[str, Any]:
    """
    Call the transportation agent to get information about transportation options.

    Args:
        query: The user's query about transportation.
        context: Additional context information that might be helpful for the transportation agent.

    Returns:
        A dictionary containing the transportation agent's response.
    """
    # Combine the query and context
    enhanced_query = query
    if context:
        enhanced_query = f"{context}\n\n{query}"

    # Create content object for the agent
    content = Content(role="user", parts=[Part(text=enhanced_query)])

    # Call the transportation agent
    response = transportation_runner.run(
        user_id="user_123", 
        session_id="transportation_session", 
        new_message=content
    )

    # Extract the response text
    response_text = ""
    if response and hasattr(response, "content") and hasattr(response.content, "parts") and len(response.content.parts) > 0:
        response_text = response.content.parts[0].text

    return {"response": response_text}
