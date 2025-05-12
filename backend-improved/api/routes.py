"""
API Routes for Travel Agent Backend.
Defines WebSocket endpoints and health check routes.
"""
import json
import logging
from typing import Any, Dict, Optional
from fastapi import WebSocket, WebSocketDisconnect, APIRouter

from config import settings
from services.session import get_session_manager
from agent.agent_handler import get_agent_response_async

# Setup logging
logger = logging.getLogger(__name__)

# Dictionary to keep track of active websocket connections
active_connections = {}

def create_router(root_agent: Any = None) -> APIRouter:
    """
    Create and configure the API router with routes.
    
    Args:
        root_agent: The root agent object (either ADK Agent or direct API handler)
        
    Returns:
        APIRouter: Configured FastAPI router
    """
    router = APIRouter()
    session_manager = get_session_manager()
    
    @router.websocket("/ws/{session_id}")
    async def websocket_endpoint(websocket: WebSocket, session_id: str):
        """WebSocket endpoint for real-time communication with the agent"""
        try:
            # Wait for client connection
            await websocket.accept()
            logger.info(f"Client #{session_id} connected")

            # Store the connection
            active_connections[session_id] = websocket

            # Send a welcome message to the client
            welcome_message = "สวัสดีค่ะ! ฉันคือผู้ช่วยวางแผนการเดินทางของคุณ\n\nคุณสามารถพิมพ์ข้อความในรูปแบบนี้:\n\nช่วยวางแผนการเดินทางท่องเที่ยวแบบละเอียดที่สุด ตามเงื่อนไขต่อไปนี้ :\n- ต้นทาง: กรุงเทพ\n- ปลายทาง: เชียงใหม่\n- ช่วงเวลาเดินทาง: วันที่: 2025-05-17 ถึงวันที่ 2025-05-22\n- งบประมาณรวม: ไม่เกิน 20,000 บาท\n\nหรือคุณสามารถถามเกี่ยวกับ:\n- ร้านอาหารแนะนำในจังหวัดต่างๆ\n- ที่พักราคาประหยัดหรือโรงแรมที่น่าสนใจ\n- สถานที่ท่องเที่ยวยอดนิยม\n- การเดินทางระหว่างจังหวัด"
            await websocket.send_text(json.dumps({"message": welcome_message}))
            await websocket.send_text(json.dumps({"turn_complete": True}))
            logger.info(f"[AGENT TO CLIENT]: {welcome_message[:50]}...")
            logger.info("[TURN COMPLETE]")

            # Set to hold processing state - avoid processing multiple messages at once
            is_processing = False

            # Process messages from the client
            try:
                while True:
                    # Receive message from client
                    user_message = await websocket.receive_text()
                    logger.info(f"[CLIENT TO AGENT]: {user_message[:50]}...")

                    # Skip processing if already handling a message
                    if is_processing:
                        logger.warning("Already processing a message, skipping")
                        await websocket.send_text(json.dumps({
                            "message": "ขออภัยค่ะ ฉันกำลังประมวลผลคำถามของคุณอยู่ กรุณารอสักครู่ค่ะ",
                            "partial": True
                        }))
                        continue

                    # Set processing flag
                    is_processing = True

                    try:
                        # Store the user message in conversation history
                        session_manager.add_user_message(session_id, user_message)
                        
                        # Store to accumulate the complete response
                        accumulated_response = ""
                        # Flag to track if this is a travel planning request
                        is_travel_plan = "ช่วยวางแผนการเดินทางท่องเที่ยว" in user_message
                        
                        # If it's a travel planning request, show a loading message
                        if is_travel_plan:
                            loading_message = "กำลังวิเคราะห์คำขอของคุณและรวบรวมข้อมูล กรุณารอสักครู่..."
                            await websocket.send_text(json.dumps({
                                "message": loading_message,
                                "partial": True
                            }))
                            logger.info(f"Sent loading message for travel plan: {loading_message}")
                        
                        # Track if we've received a final response
                        final_response_received = False
                        
                        # Process the message with get_agent_response_async
                        async for response in get_agent_response_async(
                            user_message=user_message,
                            session_id=session_id,
                            agent_type="travel",  # Default agent type
                            root_agent=root_agent
                        ):
                            if response.get("partial", False):
                                # Accumulate partial responses
                                partial_text = response.get("message", "")
                                accumulated_response += partial_text
                                
                                # For travel planning, send status updates but not content fragments
                                if is_travel_plan and partial_text.startswith("กำลัง"):
                                    await websocket.send_text(json.dumps({
                                        "message": partial_text,
                                        "partial": True
                                    }))
                                    logger.info(f"Sent status update: {partial_text[:50]}...")
                                
                            elif response.get("final", False):
                                # Mark that we've received a final response
                                final_response_received = True
                                
                                # Get the final response message
                                final_message = response.get("message", "")
                                logger.info(f"Received final response: {final_message[:100]}...")
                                
                                # If no accumulation has happened, use the final message
                                if not accumulated_response:
                                    accumulated_response = final_message
                                    
                                # Make sure this is a proper travel plan if it's a travel planning request
                                if is_travel_plan and "===== แผนการเดินทางของคุณ =====" not in accumulated_response:
                                    if "===== แผนการเดินทางของคุณ =====" in final_message:
                                        # Use the final message if it has the correct format
                                        accumulated_response = final_message
                                    elif len(accumulated_response) > 500:
                                        # Add the header if it's missing but the content is substantial
                                        accumulated_response = "\n===== แผนการเดินทางของคุณ =====\n" + accumulated_response
                                
                                # Store the agent response in conversation history
                                session_manager.add_agent_message(session_id, accumulated_response, "travel")

                                # Send final accumulated response
                                logger.info(f"Sending final response to client: {accumulated_response[:100]}...")
                                await websocket.send_text(json.dumps({
                                    "message": accumulated_response,
                                    "final": True
                                }))
                                
                                # Signal turn completion
                                await websocket.send_text(json.dumps({"turn_complete": True}))
                                logger.info(f"[AGENT TO CLIENT]: {accumulated_response[:50]}...")
                                logger.info("[TURN COMPLETE]")
                        
                        # If we didn't receive a final response, check if we have accumulated anything
                        if not final_response_received:
                            if accumulated_response:
                                # We have some accumulated content but no final response was marked
                                logger.warning("No final response received, using accumulated content")
                                
                                # Make sure this is a proper travel plan if it's a travel planning request
                                if is_travel_plan and "===== แผนการเดินทางของคุณ =====" not in accumulated_response:
                                    if len(accumulated_response) > 500:
                                        # Add the header if it's missing but the content is substantial
                                        accumulated_response = "\n===== แผนการเดินทางของคุณ =====\n" + accumulated_response
                                
                                # Store in conversation history
                                session_manager.add_agent_message(session_id, accumulated_response, "travel")
                                
                                # Send final accumulated response
                                await websocket.send_text(json.dumps({
                                    "message": accumulated_response,
                                    "final": True
                                }))
                            else:
                                # No content at all - send an error message
                                error_message = "ขออภัยค่ะ ฉันไม่สามารถประมวลผลคำขอของคุณได้ในขณะนี้ กรุณาลองใหม่อีกครั้งค่ะ"
                                session_manager.add_agent_message(session_id, error_message, "travel")
                                await websocket.send_text(json.dumps({
                                    "message": error_message,
                                    "final": True
                                }))
                            
                            # Signal turn completion
                            await websocket.send_text(json.dumps({"turn_complete": True}))
                            logger.info("[TURN COMPLETE - Fallback completion]")

                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        await websocket.send_text(json.dumps({
                            "message": f"ขออภัยค่ะ เกิดข้อผิดพลาดในการประมวลผล: {str(e)}",
                            "final": True
                        }))
                        await websocket.send_text(json.dumps({"turn_complete": True}))

                    # Reset processing flag
                    is_processing = False

            except WebSocketDisconnect:
                logger.info(f"Client #{session_id} disconnected")
                if session_id in active_connections:
                    del active_connections[session_id]

        except Exception as e:
            logger.error(f"WebSocket error: {e}")

    @router.get("/health")
    def health_check() -> Dict[str, str]:
        """Health check endpoint"""
        return {
            "status": "ok", 
            "mode": "vertex" if settings.USE_VERTEX_AI else "direct",
            "model": settings.MODEL
        }
        
    return router
