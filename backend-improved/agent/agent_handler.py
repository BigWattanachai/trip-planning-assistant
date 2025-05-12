"""
Agent Handler module for Travel Agent Backend.
Handles asynchronous agent responses and coordinates between direct API and Vertex AI modes.
"""
import os
import logging
import google.generativeai as genai
from typing import Any, Dict, List, AsyncGenerator

from config import settings
from services.session import get_session_manager
from agent.root_agent import get_adk_app, get_root_agent
from agent.tools.extract_info import extract_travel_info, classify_query
from agent.utils.sub_agent_caller import call_sub_agent

logger = logging.getLogger(__name__)

async def get_agent_response_async(
    user_message: str,
    session_id: str,
    agent_type: str = "travel",
    root_agent: Any = None,
    retry_count: int = 0
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Gets a response from the agent asynchronously.
    Works with both Vertex AI (ADK) and direct API modes.

    Args:
        user_message: The user's message
        session_id: Session identifier
        agent_type: The type of agent to use
        root_agent: The root agent instance (optional, will use global if None)
        retry_count: Number of times this function has been retried

    Yields:
        Dictionary containing response parts
    """
    try:
        # Initialize session manager
        session_manager = get_session_manager()
        
        # If root_agent is None, try to get it from the global state
        if root_agent is None:
            root_agent = get_root_agent()
        
        # Get the ADK app instance if in Vertex AI mode
        adk_app = get_adk_app() if settings.USE_VERTEX_AI else None
        
        # Check if we should use ADK or direct Gemini API
        if settings.USE_VERTEX_AI and adk_app:
            logger.info(f"Using ADK to process message for session {session_id}")
            
            # Create a valid user ID from the session ID
            user_id = f"user_{session_id}"
            accumulated_text = ""
            
            try:
                # Ensure the session exists in the ADK session service
                session_manager.ensure_adk_session(session_id)
                
                # Stream the response from the ADK app
                for event in adk_app.stream_query(
                    user_id=user_id,
                    session_id=session_id,
                    message=user_message
                ):
                    if "content" in event:
                        if "parts" in event["content"]:
                            parts = event["content"]["parts"]
                            for part in parts:
                                if "text" in part:
                                    text_part = part["text"]
                                    accumulated_text += text_part
                                    yield {"message": text_part, "partial": True}
                
                # If we have accumulated text, send it as the final response
                if accumulated_text:
                    yield {"message": accumulated_text, "final": True}
                else:
                    # Fallback response if no text was accumulated
                    yield {"message": "ขออภัยค่ะ ฉันไม่สามารถประมวลผลคำขอของคุณได้ในขณะนี้ กรุณาลองใหม่อีกครั้งค่ะ", "final": True}
            
            except Exception as e:
                logger.error(f"Error processing with ADK: {str(e)}")
                # Fall back to direct API if ADK fails
                yield {"message": "ขออภัยค่ะ มีปัญหาในการประมวลผล กำลังลองวิธีอื่น...", "partial": True}
                async for response in process_with_direct_api(user_message, session_id):
                    yield response
        
        else:
            # Use direct Gemini API
            logger.info(f"Using direct Gemini API for session {session_id}")
            
            # Check if this is a travel planning request
            is_travel_plan = "ช่วยวางแผนการเดินทางท่องเที่ยว" in user_message
            
            if is_travel_plan:
                # Call sub-agents for a complete travel plan
                yield {"message": "กำลังวิเคราะห์คำขอของคุณและรวบรวมข้อมูลจากผู้เชี่ยวชาญด้านต่างๆ...", "partial": True}
                
                # Extract destination information from the query
                travel_info = extract_travel_info(user_message)
                destination = travel_info.get("destination", "")
                logger.info(f"Extracted destination: {destination}")
                
                # Add travel info to session state
                for key, value in travel_info.items():
                    session_manager.store_state(session_id, f"user_{key}", value)
                
                # Search YouTube for travel insights
                youtube_insights = ""
                try:
                    from agent.tools.youtube_search import search_youtube_for_travel, format_youtube_insights
                    
                    if destination and destination != "ไม่ระบุ" and destination != "ภายในประเทศไทย":
                        logger.info(f"Searching YouTube for destination: {destination}")
                        yield {"message": "กำลังค้นหาข้อมูลจาก YouTube เกี่ยวกับจุดหมายปลายทาง...", "partial": True}
                        
                        youtube_results = search_youtube_for_travel(
                            query="สถานที่เที่ยว ที่พัก ที่กิน แนะนำการเดินทาง 2025",
                            destination=destination,
                            max_results=3,
                            language="th"
                        )
                        
                        # Log the YouTube search results for debugging
                        logger.info(f"YouTube search results: {youtube_results.get('success')}, videos: {len(youtube_results.get('videos', []))}, insights: {len(youtube_results.get('insights', {}))}")
                        
                        if youtube_results.get("success") and youtube_results.get("insights"):
                            youtube_insights = format_youtube_insights(youtube_results.get("insights", {}))
                            logger.info(f"YouTube insights found: {len(youtube_insights)}")
                            
                            # Store insights in session state
                            session_manager.store_state(session_id, "youtube_insights", youtube_insights)
                        else:
                            logger.warning("No YouTube insights found")
                except Exception as e:
                    logger.error(f"Error with YouTube search: {e}")
                
                # Call each sub-agent in sequence
                logger.info("Calling transportation sub-agent")
                transportation_response = call_sub_agent("transportation", user_message, session_id)
                yield {"message": "กำลังหาข้อมูลเกี่ยวกับการเดินทาง...", "partial": True}
                
                logger.info("Calling accommodation sub-agent")
                accommodation_response = call_sub_agent("accommodation", user_message, session_id)
                yield {"message": "กำลังรวบรวมข้อมูลที่พัก...", "partial": True}
                
                logger.info("Calling restaurant sub-agent")
                restaurant_response = call_sub_agent("restaurant", user_message, session_id)
                yield {"message": "กำลังหาร้านอาหารที่น่าสนใจ...", "partial": True}
                
                logger.info("Calling activity sub-agent")
                activity_response = call_sub_agent("activity", user_message, session_id)
                yield {"message": "กำลังรวบรวมข้อมูลสถานที่ท่องเที่ยวและกิจกรรมที่น่าสนใจ...", "partial": True}
                
                # Finally, call the travel planner to create a comprehensive plan
                logger.info("Calling travel planner sub-agent")
                # Include info from other sub-agents in the travel planner's input
                enhanced_query = f"""
                {user_message}

                ข้อมูลการเดินทาง:
                {transportation_response[:1000] if transportation_response else "ไม่มีข้อมูล"}

                ข้อมูลที่พัก:
                {accommodation_response[:1000] if accommodation_response else "ไม่มีข้อมูล"}

                ข้อมูลร้านอาหาร:
                {restaurant_response[:1000] if restaurant_response else "ไม่มีข้อมูล"}

                ข้อมูลสถานที่ท่องเที่ยวและกิจกรรม:
                {activity_response[:1000] if activity_response else "ไม่มีข้อมูล"}

                ข้อมูลเพิ่มเติมจาก YouTube:
                {youtube_insights if youtube_insights else "ไม่พบข้อมูลเพิ่มเติมจาก YouTube"}
                """
                
                # Store all the responses in session state
                session_manager.store_state(session_id, "transportation_response", transportation_response)
                session_manager.store_state(session_id, "accommodation_response", accommodation_response)
                session_manager.store_state(session_id, "restaurant_response", restaurant_response)
                session_manager.store_state(session_id, "activity_response", activity_response)
                
                yield {"message": "กำลังจัดทำแผนการเดินทางแบบสมบูรณ์...", "partial": True}
                
                travel_plan = call_sub_agent("travel_planner", enhanced_query, session_id)
                
                # Ensure the travel plan has the proper format
                if travel_plan and "===== แผนการเดินทางของคุณ =====" not in travel_plan:
                    travel_plan = "===== แผนการเดินทางของคุณ =====\n\n" + travel_plan
                
                # Store the travel plan in session state
                session_manager.store_state(session_id, "travel_plan", travel_plan)
                
                # Send the final comprehensive travel plan
                yield {"message": travel_plan, "final": True}
            
            else:
                # Process regular queries directly
                async for response in process_with_direct_api(user_message, session_id):
                    yield response
    
    except Exception as e:
        logger.error(f"Error getting agent response: {str(e)}")
        # Fallback response in case of error
        yield {"message": f"ขออภัยค่ะ มีข้อผิดพลาดเกิดขึ้น: {str(e)}", "final": True}

async def process_with_direct_api(user_message: str, session_id: str = None) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Process the message using direct Gemini API.
    
    Args:
        user_message: The user's message
        session_id: Session identifier
        
    Yields:
        Dictionary containing response parts
    """
    try:
        # Initialize the Gemini model
        try:
            gemini_model = genai.GenerativeModel(settings.MODEL)
            logger.info(f"Initialized Gemini model: {settings.MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            yield {"message": "ขออภัยค่ะ ไม่สามารถเชื่อมต่อกับ AI ได้ในขณะนี้", "final": True}
            return
        
        # Determine if this is a specialized query
        query_type = classify_query(user_message)
        logger.info(f"Query classified as: {query_type}")
        
        if query_type != "general":
            # Call appropriate sub-agent for specialized queries
            specialized_response = call_sub_agent(query_type, user_message, session_id)
            
            # Ensure we have a complete response
            if specialized_response:
                logger.info(f"Specialized response from {query_type} agent received: {specialized_response[:100]}...")
                # Make sure the response is properly formatted if it's a travel plan
                if query_type == "travel_planner" and "===== แผนการเดินทางของคุณ =====" not in specialized_response:
                    specialized_response = "===== แผนการเดินทางของคุณ =====\n\n" + specialized_response
                yield {"message": specialized_response, "final": True}
            else:
                logger.error(f"Empty response from {query_type} agent")
                yield {"message": "ขออภัยค่ะ ไม่สามารถประมวลผลคำขอได้ กรุณาลองใหม่อีกครั้ง", "final": True}
            return
        
        # Create a prompt for general queries
        prompt = f"""คุณคือผู้ช่วยวางแผนการเดินทางท่องเที่ยว

คำถาม: {user_message}

โปรดให้คำแนะนำที่เป็นประโยชน์ที่สุดในการตอบคำถามนี้ โดยให้ข้อมูลเกี่ยวกับการท่องเที่ยว ที่พัก ร้านอาหาร หรือกิจกรรมต่างๆ ตามที่เหมาะสม
"""
        
        logger.info(f"Sending prompt to Gemini API: {prompt[:100]}...")
        
        # Generate response from Gemini API
        response = await gemini_model.generate_content_async(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            },
        )
        
        # Get the complete response
        if hasattr(response, 'text'):
            # Direct response without streaming
            full_response = response.text
            logger.info(f"Complete response received: {full_response[:100]}...")
            yield {"message": full_response, "final": True}
        else:
            # Try to stream the response
            try:
                full_response = ""
                async for chunk in response:
                    if hasattr(chunk, 'text') and chunk.text:
                        full_response += chunk.text
                
                logger.info(f"Streamed response completed: {full_response[:100]}...")
                # Send the complete response
                if full_response:
                    yield {"message": full_response, "final": True}
                else:
                    yield {"message": "ขออภัยค่ะ ฉันไม่สามารถประมวลผลคำขอของคุณได้ในขณะนี้ กรุณาลองใหม่อีกครั้งค่ะ", "final": True}
            except Exception as e:
                logger.error(f"Error streaming response: {e}")
                yield {"message": f"ขออภัยค่ะ เกิดข้อผิดพลาดในการประมวลผล: {str(e)}", "final": True}
    
    except Exception as e:
        logger.error(f"Error with direct API: {str(e)}")
        yield {"message": f"ขออภัยค่ะ เกิดข้อผิดพลาดในการประมวลผล: {str(e)}", "final": True}
