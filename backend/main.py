import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from google.genai.types import Part, Content
from google.adk.runners import Runner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.sessions.in_memory_session_service import InMemorySessionService

# Import the root_agent (travel_coordinator)
from agents.travel_coordinator import root_agent

# Load environment variables
load_dotenv()

app = FastAPI(title="Travel A2A Backend")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

APP_NAME = "Travel A2A Application"
session_service = InMemorySessionService()

# Active WebSocket connections
active_connections = {}

def start_agent_session(session_id: str):
    """Starts an agent session"""
    # Create a Session
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=session_id,
        session_id=session_id,
    )
    
    # Create a Runner
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )
    
    # Set response modality = TEXT
    run_config = RunConfig(response_modalities=["TEXT"])
    
    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()
    
    # Start agent session
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    
    return live_events, live_request_queue

async def agent_to_client_messaging(websocket, live_events):
    """Agent to client communication"""
    try:
        async for event in live_events:
            # turn_complete
            if event.turn_complete:
                await websocket.send_text(json.dumps({"turn_complete": True}))
                print("[TURN COMPLETE]")
                
            if event.interrupted:
                await websocket.send_text(json.dumps({"interrupted": True}))
                print("[INTERRUPTED]")
                
            # Read the Content and its first Part
            part = event.content and event.content.parts and event.content.parts[0]
            
            if not part or not event.partial:
                continue
                
            # Get the text
            text = event.content and event.content.parts and event.content.parts[0].text
            
            if not text:
                continue
                
            # Send the text to the client
            await websocket.send_text(json.dumps({"message": text}))
            print(f"[AGENT TO CLIENT]: {text}")
            
            await asyncio.sleep(0)
    except Exception as e:
        print(f"Error in agent_to_client_messaging: {e}")

async def client_to_agent_messaging(websocket, live_request_queue):
    """Client to agent communication"""
    try:
        while True:
            text = await websocket.receive_text()
            content = Content(role="user", parts=[Part.from_text(text=text)])
            live_request_queue.send_content(content=content)
            print(f"[CLIENT TO AGENT]: {text}")
            
            await asyncio.sleep(0)
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in client_to_agent_messaging: {e}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.websocket("/api/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication with the agent"""
    try:
        # Wait for client connection
        await websocket.accept()
        print(f"Client #{session_id} connected")
        
        # Store the connection
        active_connections[session_id] = websocket
        
        # Start agent session
        session_id_str = str(session_id)
        live_events, live_request_queue = start_agent_session(session_id_str)
        
        # Start tasks
        agent_to_client_task = asyncio.create_task(
            agent_to_client_messaging(websocket, live_events)
        )
        client_to_agent_task = asyncio.create_task(
            client_to_agent_messaging(websocket, live_request_queue)
        )
        
        try:
            await asyncio.gather(agent_to_client_task, client_to_agent_task)
        except Exception as e:
            print(f"Error in WebSocket connection: {e}")
        finally:
            # Clean up
            if session_id in active_connections:
                del active_connections[session_id]
            print(f"Client #{session_id} disconnected")
            
    except Exception as e:
        print(f"Error in websocket_endpoint: {e}")

# API endpoints for specific agent functionalities

@app.post("/api/plan_trip")
async def plan_trip_api(
    origin: str = Body(...), 
    destination: str = Body(...),
    departure_date: str = Body(...),
    return_date: str = Body(...),
    budget: str = Body(None),
    interests: str = Body(None),
    travelers: int = Body(1)
):
    """API endpoint to plan a complete trip"""
    try:
        # In a real implementation, this would use the travel_coordinator agent
        return {
            "status": "success",
            "message": "Trip planning initiated",
            "details": {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "return_date": return_date,
                "budget": budget,
                "interests": interests,
                "travelers": travelers
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search_activities")
async def search_activities_api(
    location: str = Query(...),
    preferences: str = Query(None),
    budget: str = Query(None)
):
    """API endpoint to search for activities"""
    try:
        # In a real implementation, this would use the activity_search_agent
        return {
            "status": "success",
            "message": "Activity search initiated",
            "details": {
                "location": location,
                "preferences": preferences,
                "budget": budget
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search_restaurants")
async def search_restaurants_api(
    location: str = Query(...),
    cuisine: str = Query(None),
    budget: str = Query(None),
    dietary_restrictions: str = Query(None)
):
    """API endpoint to search for restaurants"""
    try:
        # In a real implementation, this would use the restaurant_agent
        return {
            "status": "success",
            "message": "Restaurant search initiated",
            "details": {
                "location": location,
                "cuisine": cuisine,
                "budget": budget,
                "dietary_restrictions": dietary_restrictions
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search_flights")
async def search_flights_api(
    origin: str = Query(...),
    destination: str = Query(...),
    departure_date: str = Query(...),
    return_date: str = Query(None),
    passengers: int = Query(1),
    cabin_class: str = Query("economy")
):
    """API endpoint to search for flights"""
    try:
        # In a real implementation, this would use the flight_search_agent
        return {
            "status": "success",
            "message": "Flight search initiated",
            "details": {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "return_date": return_date,
                "passengers": passengers,
                "cabin_class": cabin_class
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search_accommodations")
async def search_accommodations_api(
    location: str = Query(...),
    check_in_date: str = Query(...),
    check_out_date: str = Query(...),
    guests: int = Query(2),
    room_type: str = Query(None),
    amenities: str = Query(None),
    budget: str = Query(None)
):
    """API endpoint to search for accommodations"""
    try:
        # In a real implementation, this would use the accommodation_agent
        return {
            "status": "success",
            "message": "Accommodation search initiated",
            "details": {
                "location": location,
                "check_in_date": check_in_date,
                "check_out_date": check_out_date,
                "guests": guests,
                "room_type": room_type,
                "amenities": amenities,
                "budget": budget
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search_travel_videos")
async def search_travel_videos_api(
    destination: str = Query(...),
    content_type: str = Query(None)
):
    """API endpoint to search for travel-related YouTube videos"""
    try:
        # In a real implementation, this would use the youtube_video_agent
        return {
            "status": "success",
            "message": "Travel video search initiated",
            "details": {
                "destination": destination,
                "content_type": content_type
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
