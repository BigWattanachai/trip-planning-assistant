"""
API Routes for Travel A2A Backend
"""
import json
import sys
import pathlib
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService

# Handle imports for both running as a module and running directly
try:
    # When running as a module (python -m backend.main)
    from backend.agents.travel.travel_agent import root_agent
    from ..core.state_manager import state_manager
    from .async_agent_handler import get_agent_response_async
except (ImportError, ValueError):
    # When running directly (python main.py)
    # Add the parent directory to sys.path
    parent_dir = str(pathlib.Path(__file__).parent.parent.parent.absolute())
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)

    # Use absolute imports
    from backend.agents.travel.travel_agent import root_agent
    from backend.core.state_manager import state_manager
    from backend.api.async_agent_handler import get_agent_response_async

# Create router
router = APIRouter()

APP_NAME = "Travel Planning Assistant"

# Global session services and runner dictionaries to keep consistent sessions per client
session_services = {}
runners = {}


# No locks needed as we're not using concurrent session creation

def get_session_and_runner(session_id: str, agent_type: str = "travel"):
    """Get or create a session service and runner for a client session"""
    # Always use the root agent regardless of agent_type
    key = f"{session_id}_travel"

    if key not in session_services:
        # Create new session service and runner for this client
        print(f"Creating new session service and runner for {key}")
        session_service = InMemorySessionService()

        # Always use the root_agent which now has tools to call specialized agents
        agent = root_agent

        # Create a new runner for this session
        runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)

        # Store session services and runners
        session_services[key] = session_service
        runners[key] = runner

        # Create a session with a common user ID
        user_id = "user_123"  
        session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)

    return session_services[key], runners[key]


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication with the agent"""
    try:
        # Wait for client connection
        await websocket.accept()
        print(f"Client #{session_id} connected")

        # Get or create a session for this client
        get_session_and_runner(session_id)

        # Mapping for active connections
        active_connections = {}
        active_connections[session_id] = websocket

        # Send a welcome message to the client
        welcome_message = "สวัสดีค่ะ! ฉันคือผู้ช่วยวางแผนการเดินทางของคุณ บอกฉันหน่อยว่าคุณอยากไปเที่ยวที่ไหน และมีงบประมาณเท่าไหร่คะ?"
        await websocket.send_text(json.dumps({"message": welcome_message}))
        await websocket.send_text(json.dumps({"turn_complete": True}))
        print(f"[AGENT TO CLIENT]: {welcome_message}")
        print("[TURN COMPLETE]")

        # Set to hold processing state - avoid processing multiple messages at once
        is_processing = False

        # Process messages from the client
        try:
            while True:
                # Receive message from client
                user_message = await websocket.receive_text()
                print(f"[CLIENT TO AGENT]: {user_message}")

                # Skip processing if already handling a message
                if is_processing:
                    print("Already processing a message, skipping")
                    await websocket.send_text(json.dumps({
                        "message": "ขออภัยค่ะ ฉันกำลังประมวลผลคำถามของคุณอยู่ กรุณารอสักครู่ค่ะ",
                        "partial": True
                    }))
                    continue

                # Set processing flag
                is_processing = True

                try:
                    # Get the runner for this session
                    _, runner = get_session_and_runner(session_id)

                    # Store the user message in conversation history
                    state_manager.add_user_message(session_id, user_message)

                    # Process the message with the root agent
                    async for response in get_agent_response_async(user_message, "travel", session_id, runner):
                        # Check if this is a partial or final response
                        if response.get("partial", False):
                            # Send partial response
                            await websocket.send_text(json.dumps({
                                "message": response.get("message", ""),
                                "partial": True
                            }))
                        elif response.get("final", False):
                            # Get the final response message
                            final_message = response.get("message", "")

                            # Store the agent response in conversation history
                            state_manager.add_agent_message(session_id, final_message, "travel")

                            # Send final response
                            await websocket.send_text(json.dumps({
                                "message": final_message,
                                "final": True
                            }))
                            # Signal turn completion
                            await websocket.send_text(json.dumps({"turn_complete": True}))
                            print(f"[AGENT TO CLIENT]: {final_message}")
                            print("[TURN COMPLETE]")

                except Exception as e:
                    print(f"Error processing message: {e}")
                    await websocket.send_text(json.dumps({
                        "message": f"ขออภัยค่ะ เกิดข้อผิดพลาดในการประมวลผล: {str(e)}",
                        "final": True
                    }))
                    await websocket.send_text(json.dumps({"turn_complete": True}))

                # Reset processing flag
                is_processing = False

        except WebSocketDisconnect:
            print(f"Client #{session_id} disconnected")
            if session_id in active_connections:
                del active_connections[session_id]

    except Exception as e:
        print(f"WebSocket error: {e}")


@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
