"""
Sub-agents for the Travel Agent Backend.
Provides specialized agents for different aspects of travel planning.
"""

import logging
from typing import Any, Dict, Optional

# Configuration
from config import settings

logger = logging.getLogger(__name__)

# Initialize variables to hold agent references
# These will be populated during initialization
AccommodationAgent = None
ActivityAgent = None
RestaurantAgent = None
TransportationAgent = None
TravelPlannerAgent = None

# Function wrappers for Tavily search tools
# These are used in direct API mode
accommodation_tavily_search = None
activity_tavily_search = None 
restaurant_tavily_search = None
transportation_tavily_search = None
travel_planner_tavily_search = None

def initialize_sub_agents():
    """Initialize all sub-agents based on the current mode."""
    global AccommodationAgent, ActivityAgent, RestaurantAgent, TransportationAgent, TravelPlannerAgent
    global accommodation_tavily_search, activity_tavily_search, restaurant_tavily_search, transportation_tavily_search, travel_planner_tavily_search
    
    # Check if we should use ADK (Vertex AI) mode
    if settings.USE_VERTEX_AI:
        try:
            from agent.tools.store_state import store_state_tool
            from agent.tools.tavily_search import initialize_tavily_search_tool
            from agent.prompts.sub_agent_prompts import (
                ACCOMMODATION_AGENT_PROMPT,
                ACTIVITY_AGENT_PROMPT,
                RESTAURANT_AGENT_PROMPT, 
                TRANSPORTATION_AGENT_PROMPT,
                TRAVEL_PLANNER_AGENT_PROMPT
            )
            
            # Import ADK components
            from google.adk.agents import Agent 
            from google.adk.tools.langchain_tool import LangchainTool
            
            # Set up a callback for rate limiting
            from agent.utils.callbacks import rate_limit_callback
            
            # Initialize the Tavily search tool
            tavily_tool = initialize_tavily_search_tool()
            adk_tavily_tool = LangchainTool(tool=tavily_tool) if tavily_tool else None
            
            # Create the Accommodation Agent
            AccommodationAgent = Agent(
                model=settings.MODEL,
                name="accommodation_agent",
                description="Provides detailed accommodation recommendations based on location, budget, and preferences.",
                instruction=ACCOMMODATION_AGENT_PROMPT,
                tools=[store_state_tool] + ([adk_tavily_tool] if adk_tavily_tool else []),
                before_model_callback=rate_limit_callback,
                output_key="accommodation_response"
            )
            
            # Create the Activity Agent
            ActivityAgent = Agent(
                model=settings.MODEL,
                name="activity_agent",
                description="Recommends activities, attractions, and sightseeing opportunities.",
                instruction=ACTIVITY_AGENT_PROMPT,
                tools=[store_state_tool] + ([adk_tavily_tool] if adk_tavily_tool else []),
                before_model_callback=rate_limit_callback,
                output_key="activity_response"
            )
            
            # Create the Restaurant Agent
            RestaurantAgent = Agent(
                model=settings.MODEL,
                name="restaurant_agent",
                description="Suggests restaurants, cafes, and dining experiences based on location and preferences.",
                instruction=RESTAURANT_AGENT_PROMPT,
                tools=[store_state_tool] + ([adk_tavily_tool] if adk_tavily_tool else []),
                before_model_callback=rate_limit_callback,
                output_key="restaurant_response"
            )
            
            # Create the Transportation Agent
            TransportationAgent = Agent(
                model=settings.MODEL,
                name="transportation_agent",
                description="Provides transportation options, routes, and travel logistics information.",
                instruction=TRANSPORTATION_AGENT_PROMPT,
                tools=[store_state_tool] + ([adk_tavily_tool] if adk_tavily_tool else []),
                before_model_callback=rate_limit_callback,
                output_key="transportation_response"
            )
            
            # Create the Travel Planner Agent
            TravelPlannerAgent = Agent(
                model=settings.MODEL,
                name="travel_planner_agent",
                description="Creates comprehensive travel itineraries combining all aspects of travel planning.",
                instruction=TRAVEL_PLANNER_AGENT_PROMPT,
                tools=[store_state_tool] + ([adk_tavily_tool] if adk_tavily_tool else []),
                before_model_callback=rate_limit_callback,
                output_key="travel_plan"
            )
            
            logger.info("All ADK sub-agents initialized successfully")
            
        except ImportError as e:
            logger.error(f"Failed to import ADK components for sub-agents: {e}")
    else:
        # Direct API mode - set up Tavily search functions
        from agent.tools.tavily_search import initialize_tavily_search, tavily_search
        
        logger.info("Initializing direct API mode sub-agent tools")
        
        # Try to initialize Tavily search
        tavily_search_instance = initialize_tavily_search()
        
        if tavily_search_instance:
            # Create wrapper functions for different agent types
            def create_tavily_search_wrapper(agent_type):
                def search_wrapper(query):
                    try:
                        logger.info(f"Direct API Mode: Searching Tavily for {agent_type}: {query}")
                        result = tavily_search_instance.invoke(query)
                        logger.info(f"Direct API Mode: Tavily search successful for {agent_type}")
                        return result
                    except Exception as e:
                        logger.error(f"Direct API Mode: Tavily search error for {agent_type}: {e}")
                        return None
                return search_wrapper
            
            # Create specialized search functions for each agent type
            accommodation_tavily_search = create_tavily_search_wrapper("accommodation")
            activity_tavily_search = create_tavily_search_wrapper("activity")
            restaurant_tavily_search = create_tavily_search_wrapper("restaurant")
            transportation_tavily_search = create_tavily_search_wrapper("transportation")
            travel_planner_tavily_search = create_tavily_search_wrapper("travel_planner")
            
            logger.info("Direct API Mode: Tavily search functions created and ready for use")
        else:
            logger.warning("Direct API Mode: Tavily search not available")
            
            # Set default search function
            def default_search(query):
                logger.warning(f"Attempted to search, but Tavily is not configured: {query}")
                return None
            
            # Assign the default function to all search wrappers
            accommodation_tavily_search = default_search
            activity_tavily_search = default_search
            restaurant_tavily_search = default_search
            transportation_tavily_search = default_search
            travel_planner_tavily_search = default_search
    
    return {
        "accommodation": AccommodationAgent,
        "activity": ActivityAgent,
        "restaurant": RestaurantAgent,
        "transportation": TransportationAgent,
        "travel_planner": TravelPlannerAgent
    }
