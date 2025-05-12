"""
Sub-agents package for the Travel Agent Backend.
Provides specialized agents for different aspects of travel planning.
"""

# Import all sub-agents for easy access
try:
    from .accommodation_agent import AccommodationAgent, accommodation_tavily_search
except ImportError:
    AccommodationAgent = None
    accommodation_tavily_search = None

try:
    from .activity_agent import ActivityAgent, activity_tavily_search
except ImportError:
    ActivityAgent = None
    activity_tavily_search = None

try:
    from .restaurant_agent import RestaurantAgent, restaurant_tavily_search
except ImportError:
    RestaurantAgent = None
    restaurant_tavily_search = None

try:
    from .transportation_agent import TransportationAgent, transportation_tavily_search
except ImportError:
    TransportationAgent = None
    transportation_tavily_search = None

try:
    from .travel_planner_agent import TravelPlannerAgent, travel_planner_tavily_search
except ImportError:
    TravelPlannerAgent = None
    travel_planner_tavily_search = None
