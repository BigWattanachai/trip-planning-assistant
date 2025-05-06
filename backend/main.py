import json
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from google.genai.types import Part, Content
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from agents.travel_agent import root_agent
from agents.activity_search_agent import activity_search_agent
from agents.restaurant_agent import restaurant_agent
from state_manager import state_manager
from improved_agent_orchestrator import improved_orchestrator
from async_agent_handler import get_agent_response_async

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

APP_NAME = "Travel Planning Assistant"

# Global session services and runner dictionaries to keep consistent sessions per client
session_services = {}
runners = {}
# Lock to prevent concurrent access to session creation
session_locks = {}

def get_session_and_runner(session_id: str, agent_type: str = "travel"):
    """Get or create a session service and runner for a client session"""
    key = f"{session_id}_{agent_type}"
    
    if key not in session_services:
        # Create new session service and runner for this client
        print(f"Creating new session service and runner for {key}")
        session_service = InMemorySessionService()
        
        # Select the appropriate agent based on the agent_type - only use one agent at a time
        # This prevents multiple responses
        if agent_type == "activity":
            agent = activity_search_agent
        elif agent_type == "restaurant":
            agent = restaurant_agent
        else:
            # Default to the main travel agent - NOT using the sequential agent to avoid multiple responses
            agent = root_agent
            
        # Create a new runner for this session
        runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)
        
        # Store session services and runners
        session_services[key] = session_service
        runners[key] = runner
        
        # Create a session
        user_id = "user_123"  # Use a common user ID
        session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
    
    return session_services[key], runners[key]


async def get_agent_response_async(user_message: str, agent_type: str = "travel", session_id: str = None):
    """Gets a response from the agent asynchronously using Google ADK and the improved orchestrator"""
    try:
        # Use a common user ID
        user_id = "user_123"
        
        # Get or create session service and runner
        session_service, runner = get_session_and_runner(session_id, agent_type)
        
        accumulated_text = ""
        final_response = ""
        partial_count = 0  # Track number of partial updates to avoid excessive streaming
        
        try:
            # Use the improved orchestrator to process the message and get events
            async for event in improved_orchestrator.process_message(user_message, session_id, runner):
                # Check if this is a partial response - only send every 3rd partial to reduce message count
                if hasattr(event, 'is_partial') and event.is_partial():
                    if event.content and hasattr(event.content, 'parts') and len(event.content.parts) > 0:
                        partial_text = event.content.parts[0].text
                        accumulated_text += partial_text
                        partial_count += 1
                        
                        # Only send partial updates occasionally to avoid flooding
                        if partial_count % 3 == 0 and len(partial_text) > 5:
                            yield {"message": partial_text, "partial": True}
                
                # Check if this is the final response
                if hasattr(event, 'is_final_response') and event.is_final_response():
                    if event.content and hasattr(event.content, 'parts') and len(event.content.parts) > 0:
                        final_response = event.content.parts[0].text
                        print(f"Final response: {final_response}")
                        yield {"message": final_response, "final": True}
                
                # Process function calls if any - but don't send to client
                if hasattr(event, 'get_function_calls'):
                    function_calls = event.get_function_calls()
                    for function_call in function_calls:
                        print(f"Function call: {function_call.name}")
                        print(f"Arguments: {function_call.args}")
                
                # Process function responses if any - but don't send to client
                if hasattr(event, 'get_function_responses'):
                    function_responses = event.get_function_responses()
                    for function_response in function_responses:
                        print(f"Function response: {function_response.name}")
                        print(f"Result: {function_response.response}")
        
        except Exception as inner_e:
            print(f"Error during run_async: {inner_e}")
            yield {"message": f"ขออภัยค่ะ เกิดข้อผิดพลาดขณะประมวลผล: {str(inner_e)}", "final": True}
            return
        
        # If we don't get a final response, use the accumulated text or a default message
        if not final_response:
            final_message = accumulated_text or "ขออภัยค่ะ ฉันยังไม่เข้าใจคำถามของคุณ กรุณาถามใหม่อีกครั้งค่ะ"
            yield {"message": final_message, "final": True}
            
    except Exception as e:
        print(f"Error getting agent response asynchronously: {e}")
        # Fallback response in case of error
        yield {"message": f"ขออภัยค่ะ มีข้อผิดพลาดเกิดขึ้น: {str(e)}", "final": True}


@app.websocket("/api/ws/{session_id}")
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

                is_processing = True
                try:
                    # Use improved orchestrator to classify user intent with session context
                    detected_agent_type = improved_orchestrator.classify_intent(user_message, session_id)
                    print(f"[INTENT CLASSIFICATION]: Detected intent as '{detected_agent_type}'")
                    
                    # Override agent_type with detected type for better routing
                    agent_type = detected_agent_type
                    
                    # Get streamed responses from the appropriate agent
                    async for response_part in get_agent_response_async(user_message, agent_type=agent_type, session_id=session_id):
                        # Send response part to client
                        if "partial" in response_part and response_part["partial"]:
                            # Send streaming response
                            await websocket.send_text(json.dumps({"message": response_part["message"], "partial": True}))
                            print(f"[AGENT TO CLIENT (STREAMING)]: {response_part['message']}")
                        elif "final" in response_part and response_part["final"]:
                            # Send final response
                            await websocket.send_text(json.dumps({"message": response_part["message"]}))
                            await websocket.send_text(json.dumps({"turn_complete": True}))
                            print(f"[AGENT TO CLIENT (FINAL)]: {response_part['message']}")
                            print("[TURN COMPLETE]")
                finally:
                    is_processing = False

        except WebSocketDisconnect:
            print(f"Client #{session_id} disconnected")
        except Exception as e:
            print(f"Error processing client message: {e}")
            # Send error message to client
            try:
                await websocket.send_text(json.dumps({"message": f"ขออภัยค่ะ มีข้อผิดพลาดเกิดขึ้น: {str(e)}"}))
                await websocket.send_text(json.dumps({"turn_complete": True}))
            except Exception:
                pass
        finally:
            # Clean up active connections
            if session_id in active_connections:
                del active_connections[session_id]
            # Don't delete session or runner to maintain state between reconnections
            print(f"Client #{session_id} disconnected, but keeping session")

    except Exception as e:
        print(f"Error in websocket_endpoint: {e}")
        # Send error message to client if connection is still open
        try:
            await websocket.send_text(json.dumps({"message": f"ขออภัยค่ะ มีข้อผิดพลาดเกิดขึ้น: {str(e)}"}))
            await websocket.send_text(json.dumps({"turn_complete": True}))
        except Exception:
            pass


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/agents")
async def list_agents():
    """List available agents"""
    return {
        "agents": [
            {
                "id": "travel",
                "name": "Travel Planning Assistant",
                "description": "General travel planning and recommendations"
            },
            {
                "id": "activity",
                "name": "Activity Search Assistant",
                "description": "Find activities and attractions in a destination"
            },
            {
                "id": "restaurant",
                "name": "Restaurant Recommendation Assistant",
                "description": "Find restaurants and food experiences in a destination"
            }
        ]
    }


@app.websocket("/api/ws/{session_id}/{agent_type}")
async def agent_websocket_endpoint(websocket: WebSocket, session_id: str, agent_type: str):
    """WebSocket endpoint for real-time communication with a specific agent"""
    try:
        # Wait for client connection
        await websocket.accept()
        print(f"Client #{session_id} connected to {agent_type} agent")
        
        # Get or create a session for this client
        get_session_and_runner(session_id, agent_type)

        # Mapping for active connections
        active_connections = {}
        connection_key = f"{session_id}_{agent_type}"
        active_connections[connection_key] = websocket
        
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

                is_processing = True
                try:
                    # Handle specialized agent intent detection with improved orchestrator
                    if state_manager.is_follow_up_question(session_id, user_message):
                        detected_agent_type = improved_orchestrator.classify_intent(user_message, session_id)
                        print(f"[INTENT CLASSIFICATION FOR SPECIALIZED AGENT]: Detected intent as '{detected_agent_type}'")

                        # Keep using the specialized agent that the user connected to 
                        # unless we're in a follow-up context and should switch
                        if detected_agent_type != agent_type and detected_agent_type != "travel":
                            print(f"Switching from {agent_type} to {detected_agent_type} for follow-up query")
                            agent_type = detected_agent_type
                    
                    # Get streamed responses from agent
                    async for response_part in get_agent_response_async(user_message, agent_type, session_id):
                        # Send response part to client
                        if "partial" in response_part and response_part["partial"]:
                            # Send streaming response
                            await websocket.send_text(json.dumps({"message": response_part["message"], "partial": True}))
                            print(f"[AGENT TO CLIENT (STREAMING)]: {response_part['message']}")
                        elif "final" in response_part and response_part["final"]:
                            # Send final response
                            await websocket.send_text(json.dumps({"message": response_part["message"]}))
                            await websocket.send_text(json.dumps({"turn_complete": True}))
                            print(f"[AGENT TO CLIENT (FINAL)]: {response_part['message']}")
                            print("[TURN COMPLETE]")
                finally:
                    is_processing = False

        except WebSocketDisconnect:
            print(f"Client #{session_id} disconnected from {agent_type} agent")
        except Exception as e:
            print(f"Error processing client message: {e}")
            # Send error message to client
            try:
                await websocket.send_text(json.dumps({"message": f"ขออภัยค่ะ มีข้อผิดพลาดเกิดขึ้น: {str(e)}"}))
                await websocket.send_text(json.dumps({"turn_complete": True}))
            except Exception:
                pass
        finally:
            # Clean up active connections
            if connection_key in active_connections:
                del active_connections[connection_key]
            # Don't delete session or runner to maintain state between reconnections
            print(f"Client #{session_id} disconnected from {agent_type} agent, but keeping session")

    except Exception as e:
        print(f"Error in agent_websocket_endpoint: {e}")
        # Send error message to client if connection is still open
        try:
            await websocket.send_text(json.dumps({"message": f"ขออภัยค่ะ มีข้อผิดพลาดเกิดขึ้น: {str(e)}"}))
            await websocket.send_text(json.dumps({"turn_complete": True}))
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
