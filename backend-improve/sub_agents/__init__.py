"""
Sub-agents package for Travel A2A Backend (Improved).
This package contains the sub-agents used by the root agent.
"""

# For ADK mode, try to import agents
import os
import logging
import sys
import pathlib

# Configure logging
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to allow imports
parent_dir = str(pathlib.Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Add current directory to sys.path
current_dir = str(pathlib.Path(__file__).parent.absolute())
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Only attempt to import sub-agents if we're in Vertex AI mode
if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes"):
    # Initialize sub-agent variables
    AccommodationAgent = None
    ActivityAgent = None
    RestaurantAgent = None
    TransportationAgent = None
    TravelPlannerAgent = None
    
    # Try to import each sub-agent individually
    try:
        from .accommodation_agent import AccommodationAgent
        logger.info("Successfully imported AccommodationAgent")
    except ImportError as e:
        logger.warning(f"Failed to import AccommodationAgent: {e}")
        AccommodationAgent = None
    
    try:
        from .activity_agent import ActivityAgent
        logger.info("Successfully imported ActivityAgent")
    except ImportError as e:
        logger.warning(f"Failed to import ActivityAgent: {e}")
        ActivityAgent = None
    
    try:
        from .restaurant_agent import RestaurantAgent
        logger.info("Successfully imported RestaurantAgent")
    except ImportError as e:
        logger.warning(f"Failed to import RestaurantAgent: {e}")
        RestaurantAgent = None
    
    try:
        from .transportation_agent import TransportationAgent
        logger.info("Successfully imported TransportationAgent")
    except ImportError as e:
        logger.warning(f"Failed to import TransportationAgent: {e}")
        TransportationAgent = None
    
    try:
        from .travel_planner_agent import TravelPlannerAgent
        logger.info("Successfully imported TravelPlannerAgent")
    except ImportError as e:
        logger.warning(f"Failed to import TravelPlannerAgent: {e}")
        TravelPlannerAgent = None
    
    # Create a list of successfully imported sub-agents
    __all__ = []
    if AccommodationAgent: __all__.append('AccommodationAgent')
    if ActivityAgent: __all__.append('ActivityAgent')
    if RestaurantAgent: __all__.append('RestaurantAgent')
    if TransportationAgent: __all__.append('TransportationAgent')
    if TravelPlannerAgent: __all__.append('TravelPlannerAgent')
    
    logger.info(f"Imported {len(__all__)} sub-agents successfully")
else:
    logger.info("Direct API Mode: Not importing sub-agents")
    AccommodationAgent = None
    ActivityAgent = None
    RestaurantAgent = None
    TransportationAgent = None
    TravelPlannerAgent = None
    
    __all__ = []
