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
        welcome_message = "สวัสดีค่ะ! ฉันคือผู้ช่วยวางแผนการเดินทางของคุณ\n\nคุณสามารถพิมพ์ข้อความในรูปแบบนี้:\n\nช่วยวางแผนการเดินทางท่องเที่ยวแบบละเอียดที่สุด ตามเงื่อนไขต่อไปนี้ :\n- ต้นทาง: กรุงเทพ\n- ปลายทาง: เชียงใหม่\n- ช่วงเวลาเดินทาง: วันที่: 2025-05-17 ถึงวันที่ 2025-05-22\n- งบประมาณรวม: ไม่เกิน 20,000 บาท\n\nหรือคุณสามารถถามเกี่ยวกับ:\n- ร้านอาหารแนะนำในจังหวัดต่างๆ\n- ที่พักราคาประหยัดหรือโรงแรมที่น่าสนใจ\n- สถานที่ท่องเที่ยวยอดนิยม\n- การเดินทางระหว่างจังหวัด"
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
                    
                    # Check if this is a travel planning request
                    is_travel_plan = "ช่วยวางแผนการเดินทางท่องเที่ยว" in user_message
                    if not is_travel_plan and len(user_message.split()) <= 10:
                        # Check if this is a follow-up to a travel planning request
                        previous_messages = state_manager.get_conversation_history(session_id, max_messages=3)
                        for message in previous_messages:
                            if message.get("role") == "user":
                                prev_content = message.get("content", "")
                                if "ช่วยวางแผนการเดินทางท่องเที่ยว" in prev_content:
                                    is_travel_plan = True
                                    break
                    
                    print(f"Is travel plan: {is_travel_plan}")

                    # Process the message with the root agent
                    final_message_sent = False
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

                            # Check if this is a travel plan but missing the marker
                            if is_travel_plan and "===== แผนการเดินทางของคุณ =====" not in final_message:
                                print("Checking if this is a complete travel plan without marker...")
                                
                                # If this is a short response like "please wait" or "I'm searching", treat as partial
                                if len(final_message) < 500 and any(phrase in final_message for phrase in [
                                    "รอสักครู่", "กำลังค้นหา", "กำลังวางแผน", "กำลังจัดทำ", "ขออภัย", 
                                    "ได้รวบรวมข้อมูล", "ดิฉันได้รวบรวม", "จะช่วยวางแผน", "ทำการค้นหา"]):
                                    print("This appears to be a 'please wait' message, sending as partial")
                                    await websocket.send_text(json.dumps({
                                        "message": final_message,
                                        "partial": True
                                    }))
                                    continue
                                
                                # If it's asking a question for more details, let it through as final
                                if "?" in final_message or "คะ?" in final_message or "ไหม" in final_message:
                                    print("This appears to be a question, sending as final")
                                    # Let this pass through as a final message
                                    pass
                                # For very short responses that are not questions or "please wait", also treat as partial
                                elif len(final_message) < 300:
                                    print("This is a very short response, sending as partial")
                                    await websocket.send_text(json.dumps({
                                        "message": final_message,
                                        "partial": True
                                    }))
                                    continue
                                # For longer responses (that are not waiting messages), replace with a structured marker
                                elif len(final_message) > 1000:
                                    print("This is a substantial response, adding travel plan marker")
                                    # Add the missing marker to the message
                                    if not final_message.startswith("\n===== แผนการเดินทางของคุณ =====\n"):
                                        final_message = "\n===== แผนการเดินทางของคุณ =====\n" + final_message
                            
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
                            final_message_sent = True

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
