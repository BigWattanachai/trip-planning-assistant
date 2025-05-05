from typing import Optional
# ...existing code...

@router.post("/create")
async def create_itinerary_route(
    location: str,
    start_date: str,
    end_date: str,
    budget: int,
    interests: Optional[str] = None,
    trip_type: Optional[str] = None,
    # ...other parameters...
):
    # ...existing code...
