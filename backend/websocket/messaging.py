from typing import Optional, Dict, Any
# ...existing code...

async def agent_to_client_messaging(client_id: str, websocket: WebSocket):
    try:
        # ...existing code...
        # When calling create_itinerary, make sure to handle None values properly
        # For example:
        # result = await create_itinerary(
        #     location=location,
        #     start_date=start_date,
        #     end_date=end_date,
        #     budget=budget,
        #     interests=interests if interests else "",  # Convert None to empty string if needed
        #     # ...other parameters...
        # )
        # ...existing code...
    except Exception as e:
        print(f"Error in agent_to_client_messaging: {e}")
        # Handle error appropriately, maybe send error message to client
        # ...existing code...
