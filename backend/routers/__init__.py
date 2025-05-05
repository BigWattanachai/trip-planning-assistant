from .activity_router import router as activity_router
from .restaurant_router import router as restaurant_router
from .flight_router import router as flight_router
from .accommodation_router import router as accommodation_router
from .video_router import router as video_router
from .travel_plan_router import router as travel_plan_router

__all__ = [
    'activity_router',
    'restaurant_router',
    'flight_router',
    'accommodation_router',
    'video_router',
    'travel_plan_router'
]
