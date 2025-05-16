"""
Async Agent Handler: Module for handling asynchronous agent responses
"""
import os
import sys
import pathlib
import logging
import json
from typing import Dict, Any, AsyncGenerator, Optional
from dotenv import load_dotenv

# Setup enhanced logging with no truncation
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
# Disable log truncation
logging.getLogger().handlers[0].terminator = "\n"
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Add the parent directory to sys.path to allow imports
parent_dir = str(pathlib.Path(__file__).parent.parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import call_sub_agent function
try:
    from agent import call_sub_agent
    logger.info("Successfully imported call_sub_agent from agent")
except ImportError:
    logger.error("Failed to import call_sub_agent function")
    # Define a fallback function
    def call_sub_agent(agent_type, query, session_id=None):
        logger.error(f"Fallback call_sub_agent: {agent_type}")
        return f"Could not call {agent_type} agent"

# Import state manager
try:
    from core.state_manager import state_manager
    logger.info("Successfully imported state_manager from core.state_manager")
except ImportError:
    logger.error("Failed to import state_manager")
    # Create a simple state manager as fallback
    class SimpleStateManager:
        def __init__(self):
            self.session_states = {}
        
        def store_state(self, session_id, key, value):
            if session_id not in self.session_states:
                self.session_states[session_id] = {}
            self.session_states[session_id][key] = value
            
        def get_state(self, session_id, key, default=None):
            if session_id not in self.session_states:
                return default
            return self.session_states[session_id].get(key, default)
    
    state_manager = SimpleStateManager()

# Add the current directory's parent to sys.path
current_parent = str(pathlib.Path(__file__).parent.parent.absolute())
if current_parent not in sys.path:
    sys.path.append(current_parent)

# Add current directory to sys.path
current_dir = str(pathlib.Path(__file__).parent.absolute())
if current_dir not in sys.path:
    sys.path.append(current_dir)

# No external search tools are being used

# Determine if using Vertex AI or direct Gemini API
USE_VERTEX_AI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes")
MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")

# Configure the Gemini API for Direct mode
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    logger.info("Configuring Gemini API with provided key")
    import google.generativeai as genai
    genai.configure(api_key=api_key)
else:
    logger.warning("GOOGLE_API_KEY not set. Direct API mode may not work.")

# Initialize the Gemini model for direct API access
gemini_model = None
try:
    import google.generativeai as genai
    gemini_model = genai.GenerativeModel(MODEL)
    logger.info(f"Initialized Gemini model: {MODEL}")
except Exception as e:
    logger.error(f"Failed to initialize Gemini model: {e}")

# Conditional imports based on mode
adk_app = None
if USE_VERTEX_AI:
    try:
        # Try to import the root agent from specific locations
        from agent import root_agent
        logger.info("Successfully imported root_agent from agent module")

        # Import ADK components if root_agent is available
        if root_agent is not None:
            from vertexai.preview.reasoning_engines import AdkApp
            try:
                adk_app = AdkApp(agent=root_agent, enable_tracing=True)
                logger.info("ADK App initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize ADK App: {e}")
                adk_app = None
    except ImportError as e:
        logger.error(f"Failed to import ADK components: {e}")
        USE_VERTEX_AI = False
        adk_app = None
else:
    logger.info("Running in direct API mode (no ADK)")

    # Import the call_sub_agent function for direct API mode
    try:
        # Only import from agent
        from agent import call_sub_agent, extract_travel_info
        logger.info("Successfully imported call_sub_agent from agent")
    except ImportError:
        logger.error("Failed to import call_sub_agent function")

        # Define a basic version in case imports fail
        def call_sub_agent(agent_type, query, session_id=None):
            logger.error(f"Fallback call_sub_agent: {agent_type}")
            return f"Could not call {agent_type} agent"

        def extract_travel_info(query):
            return {
                "origin": "กรุงเทพ",
                "destination": "ไม่ระบุ",
                "start_date": "ไม่ระบุ",
                "end_date": "ไม่ระบุ",
                "budget": "ไม่ระบุ"
            }

async def get_agent_response_async(
    user_message: str,
    agent_type: str = "travel",
    session_id: Optional[str] = None,
    runner = None,
    retry_count: int = 0
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Gets a response from the agent asynchronously

    Args:
        user_message: The user's message
        agent_type: The type of agent to use
        session_id: Session identifier
        runner: The runner instance (for ADK mode)
        retry_count: Number of times this function has been retried

    Yields:
        Dictionary containing response parts
    """
    try:
        # Check if we should use ADK or direct Gemini API
        if USE_VERTEX_AI and adk_app:
            logger.info(f"Using ADK to process message for session {session_id}")

            user_id = f"user_{session_id}"
            accumulated_text = ""

            try:
                # Improved ADK session management to fix "Session not found" errors
                try:
                    try:
                        # First try to check if session exists
                        adk_app.get_session(user_id=user_id, session_id=session_id)
                        logger.info(f"ADK session exists for user_id={user_id}, session_id={session_id}")
                    except Exception as session_err:
                        # If checking session fails, create a new one
                        logger.info(f"ADK session check failed: {session_err}, creating new session")
                        adk_app.create_session(user_id=user_id, session_id=session_id)
                        logger.info(f"Created new ADK session for user_id={user_id}, session_id={session_id}")
                except Exception as create_err:
                    logger.error(f"Failed to create ADK session: {create_err}")
                    # Try with fresh session ID as a last resort
                    from datetime import datetime
                    fallback_session_id = f"{session_id}_fb_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    logger.info(f"Attempting with fallback session_id={fallback_session_id}")
                    try:
                        adk_app.create_session(user_id=user_id, session_id=fallback_session_id)
                        session_id = fallback_session_id  # Use the new session ID from now on
                        logger.info(f"Successfully created fallback ADK session")
                    except Exception as fallback_err:
                        logger.error(f"Even fallback session creation failed: {fallback_err}")
                        raise

                # Add robust error handling around the stream_query method
                logger.info(f"Sending message to ADK stream_query: '{user_message[:50]}...'")

                # Add timeout handling for stream_query
                import asyncio
                # Process the message through ADK app with timeout monitoring
                response_started = False
                for event in adk_app.stream_query(
                    user_id=user_id,
                    session_id=session_id,
                    message=user_message
                ):
                    # Log detailed event information
                    response_started = True
                    logger.info(f"Received ADK event: {type(event)}, keys: {event.keys() if hasattr(event, 'keys') else 'No keys method'}")

                    # Handle content in response
                    if "content" in event:
                        if "parts" in event["content"]:
                            parts = event["content"]["parts"]
                            for part in parts:
                                if "text" in part:
                                    text_part = part["text"]
                                    accumulated_text += text_part

                                    # Check for sub-agent call tags in partial responses
                                    import re
                                    sub_agent_calls = re.findall(r'\[CALL_SUB_AGENT:(\w+):([^\]]+)\]', text_part)

                                    # Process any sub-agent calls in partial responses
                                    for agent_type, query in sub_agent_calls:
                                        logger.info(f"Detected sub-agent call in partial response: {agent_type} with query: {query}")
                                        try:
                                            # Call the sub-agent
                                            sub_agent_response = call_sub_agent(agent_type, query, session_id)

                                            # Replace the tag with the response
                                            tag = f"[CALL_SUB_AGENT:{agent_type}:{query}]"
                                            text_part = text_part.replace(tag, f"\n\n**{agent_type.upper()} AGENT RESPONSE:**\n{sub_agent_response}\n\n")
                                            accumulated_text = accumulated_text.replace(tag, f"\n\n**{agent_type.upper()} AGENT RESPONSE:**\n{sub_agent_response}\n\n")
                                        except Exception as e:
                                            logger.error(f"Error calling sub-agent {agent_type} in partial response: {e}")

                                    yield {"message": text_part, "partial": True}
                                    logger.info(f"Yielded partial response: {text_part[:50]}...")

                    # Log any tool outputs received
                    if "toolOutputs" in event:
                        logger.info(f"Received tool outputs: {event['toolOutputs']}")

                if not response_started:
                    logger.warning("ADK stream_query completed but no events were received")

                # If we have accumulated text, send it as the final response
                if accumulated_text:
                    # Check for sub-agent call tags
                    import re
                    sub_agent_calls = re.findall(r'\[CALL_SUB_AGENT:(\w+):([^\]]+)\]', accumulated_text)

                    # Process any sub-agent calls
                    for agent_type, query in sub_agent_calls:
                        logger.info(f"Detected sub-agent call: {agent_type} with query: {query}")
                        try:
                            # Call the sub-agent
                            sub_agent_response = call_sub_agent(agent_type, query, session_id)

                            # Replace the tag with the response
                            tag = f"[CALL_SUB_AGENT:{agent_type}:{query}]"
                            accumulated_text = accumulated_text.replace(tag, f"\n\n**{agent_type.upper()} AGENT RESPONSE:**\n{sub_agent_response}\n\n")
                        except Exception as e:
                            logger.error(f"Error calling sub-agent {agent_type}: {e}")

                    logger.info(f"Sending final accumulated response ({len(accumulated_text)} chars)")
                    yield {"message": accumulated_text, "final": True}
                else:
                    # Fallback response if no text was accumulated
                    logger.warning("No text was accumulated from ADK response")
                    yield {"message": "ขออภัยค่ะ ฉันไม่สามารถประมวลผลคำขอของคุณได้ในขณะนี้ กรุณาลองใหม่อีกครั้งค่ะ", "final": True}
            except Exception as e:
                logger.error(f"Error processing with ADK: {str(e)}")
                logger.error(f"Error type: {type(e).__name__}")

                # Provide more specific error message for session errors
                error_message = "ขออภัยค่ะ มีปัญหาในการประมวลผล กำลังลองวิธีอื่น..."
                if "session not found" in str(e).lower():
                    logger.error("ADK SESSION NOT FOUND error detected")
                    error_message = "ขออภัยค่ะ เซสชันหายไป กำลังสร้างเซสชันใหม่และลองอีกครั้ง..."

                    # Try once more with a fresh session if it's a session error
                    if retry_count < 1:  # Only retry once
                        logger.info("Retrying with fresh session...")
                        try:
                            from datetime import datetime
                            new_session_id = f"{session_id}_retry_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                            logger.info(f"Creating fresh session with ID: {new_session_id}")
                            # Try recursively with new session and increment retry counter
                            async for retry_response in get_agent_response_async(user_message, agent_type, new_session_id, runner, retry_count + 1):
                                yield retry_response
                            return  # Exit after retry completes
                        except Exception as retry_err:
                            logger.error(f"Retry with fresh session also failed: {retry_err}")

                # Fall back to direct API if ADK fails or after retry
                yield {"message": error_message, "partial": True}
                logger.info("Falling back to direct API mode after ADK failure")
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

                # No external search is being used
                destination_info = ""

                # Call each sub-agent in sequence with detailed logging
                logger.info("Calling transportation sub-agent")
                logger.info(f"Transportation sub-agent input: {user_message}")
                transportation_response = call_sub_agent("transportation", user_message, session_id)
                logger.info(f"Transportation sub-agent response (FULL): {transportation_response}")
                yield {"message": "กำลังหาข้อมูลเกี่ยวกับการเดินทาง...", "partial": True}

                logger.info("Calling accommodation sub-agent")
                logger.info(f"Accommodation sub-agent input: {user_message}")
                accommodation_response = call_sub_agent("accommodation", user_message, session_id)
                logger.info(f"Accommodation sub-agent response (FULL): {accommodation_response}")
                yield {"message": "กำลังรวบรวมข้อมูลที่พัก...", "partial": True}

                logger.info("Calling restaurant sub-agent")
                logger.info(f"Restaurant sub-agent input: {user_message}")
                restaurant_response = call_sub_agent("restaurant", user_message, session_id)
                logger.info(f"Restaurant sub-agent response (FULL): {restaurant_response}")
                yield {"message": "กำลังหาร้านอาหารที่น่าสนใจ...", "partial": True}

                logger.info("Calling activity sub-agent")
                logger.info(f"Activity sub-agent input: {user_message}")
                activity_response = call_sub_agent("activity", user_message, session_id)
                logger.info(f"Activity sub-agent response (FULL): {activity_response}")
                yield {"message": "กำลังรวบรวมข้อมูลสถานที่ท่องเที่ยวและกิจกรรมที่น่าสนใจ...", "partial": True}

                # Call our new YouTube insight agent
                logger.info("Calling YouTube insight sub-agent")
                logger.info(f"YouTube insight sub-agent input: {user_message}")
                youtube_insight_response_raw = call_sub_agent("youtube_insight", user_message, session_id)

                # Parse the JSON response
                try:
                    import json
                    youtube_insight_json = json.loads(youtube_insight_response_raw)

                    # Extract the readable format if available
                    if isinstance(youtube_insight_json, dict) and "readable" in youtube_insight_json:
                        youtube_insight_readable = youtube_insight_json["readable"]
                        youtube_insight_data = youtube_insight_json["data"]
                        logger.info(f"YouTube insight sub-agent readable response: {youtube_insight_readable[:1000]}...")
                        logger.info(f"YouTube insight sub-agent data response: {json.dumps(youtube_insight_data, ensure_ascii=False)[:1000]}...")
                        # Use the readable format for the enhanced query
                        youtube_insight_response = youtube_insight_readable
                    else:
                        # Fallback to the raw response
                        logger.warning("YouTube insight response does not contain readable format")
                        youtube_insight_response = youtube_insight_response_raw
                except Exception as e:
                    logger.error(f"Error parsing YouTube insight response: {e}")
                    youtube_insight_response = youtube_insight_response_raw

                yield {"message": "กำลังวิเคราะห์ข้อมูลจากวิดีโอ YouTube เกี่ยวกับจุดหมายปลายทาง...", "partial": True}

                # Finally, call the travel planner to create a comprehensive plan
                logger.info("Calling travel planner sub-agent")
                # Include info from other sub-agents in the travel planner's input
                enhanced_query = f"""
                {user_message}

                ข้อมูลการเดินทาง:
                {transportation_response[:5000] if transportation_response else "ไม่มีข้อมูล"}

                ข้อมูลที่พัก:
                {accommodation_response[:5000] if accommodation_response else "ไม่มีข้อมูล"}

                ข้อมูลร้านอาหาร:
                {restaurant_response[:5000] if restaurant_response else "ไม่มีข้อมูล"}

                ข้อมูลสถานที่ท่องเที่ยวและกิจกรรม:
                {activity_response[:5000] if activity_response else "ไม่มีข้อมูล"}

                ข้อมูลเชิงลึกจาก YouTube:
                {youtube_insight_response[:10000] if youtube_insight_response else "ไม่มีข้อมูล"}
                """

                # Log the enhanced query for debugging (full version)
                logger.info(f"Enhanced query for travel planner (FULL): {enhanced_query}")

                # Also log each section separately for better readability
                logger.info("--- ENHANCED QUERY SECTIONS ---")
                logger.info(f"Original user message: {user_message}")
                logger.info(f"Transportation info: {transportation_response[:1000]}..." if transportation_response else "Transportation info: None")
                logger.info(f"Accommodation info: {accommodation_response[:1000]}..." if accommodation_response else "Accommodation info: None")
                logger.info(f"Restaurant info: {restaurant_response[:1000]}..." if restaurant_response else "Restaurant info: None")
                logger.info(f"Activity info: {activity_response[:1000]}..." if activity_response else "Activity info: None")
                logger.info(f"YouTube insight info: {youtube_insight_response[:1000]}..." if youtube_insight_response else "YouTube insight info: None")
                logger.info("--- END OF ENHANCED QUERY SECTIONS ---")

                # Save the enhanced query to a file for easier inspection
                try:
                    import os
                    from datetime import datetime
                    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
                    os.makedirs(log_dir, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    log_file = os.path.join(log_dir, f"enhanced_query_{timestamp}.txt")
                    with open(log_file, "w", encoding="utf-8") as f:
                        f.write(f"SESSION ID: {session_id}\n\n")
                        f.write(f"ORIGINAL QUERY:\n{user_message}\n\n")
                        f.write(f"ENHANCED QUERY:\n{enhanced_query}\n")
                    logger.info(f"Enhanced query saved to file: {log_file}")
                except Exception as e:
                    logger.error(f"Failed to save enhanced query to file: {e}")

                # Store the enhanced query in state manager for potential updates later
                state_manager.store_state(session_id, "last_enhanced_query", enhanced_query)

                yield {"message": "กำลังจัดทำแผนการเดินทางแบบสมบูรณ์...", "partial": True}

                logger.info("Calling travel planner sub-agent with enhanced query")
                travel_plan = call_sub_agent("travel_planner", enhanced_query, session_id)
                logger.info("Travel planner sub-agent call completed")

                # Ensure the travel plan has the proper format
                if travel_plan and "===== แผนการเดินทางของคุณ =====" not in travel_plan:
                    travel_plan = "===== แผนการเดินทางของคุณ =====\n\n" + travel_plan

                # Log the complete travel plan
                logger.info(f"Travel plan created (FULL): {travel_plan}")

                # Save the travel plan to a file for easier inspection
                try:
                    import os
                    from datetime import datetime
                    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
                    os.makedirs(log_dir, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    log_file = os.path.join(log_dir, f"travel_plan_{timestamp}.txt")
                    with open(log_file, "w", encoding="utf-8") as f:
                        f.write(f"SESSION ID: {session_id}\n\n")
                        f.write(f"ORIGINAL QUERY:\n{user_message}\n\n")
                        f.write(f"TRAVEL PLAN:\n{travel_plan}\n")
                    logger.info(f"Travel plan saved to file: {log_file}")
                except Exception as e:
                    logger.error(f"Failed to save travel plan to file: {e}")

                # Store the travel plan in state manager for potential updates later
                state_manager.store_state(session_id, "last_travel_plan", travel_plan)

                # Send the final comprehensive travel plan - CRITICAL FIX: ensure this is marked as final
                yield {"message": travel_plan, "final": True}
            else:
                # Process regular queries directly
                async for response in process_with_direct_api(user_message, session_id):
                    yield response

    except Exception as e:
        logger.error(f"Error getting agent response: {str(e)}")
        # Fallback response in case of error
        yield {"message": f"ขออภัยค่ะ มีข้อผิดพลาดเกิดขึ้น: {str(e)}", "final": True}

async def process_with_direct_api(user_message: str, session_id: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
    """Process the message using direct Gemini API"""
    try:
        if not gemini_model:
            raise ValueError("Gemini model not initialized")

        # Determine if this is a specialized query
        query_type = classify_query(user_message)
        logger.info(f"Query classified as: {query_type}")

        # No external search is being used
        search_results = None

        if query_type != "general":
            # Check if this is a plan update request
            if query_type == "plan_update":
                # Retrieve the last travel plan
                last_travel_plan = state_manager.get_state(session_id, "last_travel_plan")
                if not last_travel_plan:
                    logger.warning("No previous travel plan found for update")
                    yield {"message": "ขออภัยค่ะ ไม่พบแผนการเดินทางล่าสุดของคุณ กรุณาสร้างแผนการเดินทางใหม่ก่อนค่ะ", "final": True}
                    return
                
                # Get the last enhanced query
                last_enhanced_query = state_manager.get_state(session_id, "last_enhanced_query")
                if not last_enhanced_query:
                    logger.warning("No previous enhanced query found")
                    # Create a simple enhanced query if not found
                    last_enhanced_query = "กรุณาสร้างแผนการเดินทางใหม่"
                
                # Create the updated query for travel planner with clearer instructions
                updated_query = f"""
                {last_enhanced_query}

                **คำขอปรับปรุงแผนจากผู้ใช้:**
                {user_message}

                **แผนการเดินทางล่าสุด:**
                {last_travel_plan}

                คำแนะนำในการปรับปรุงแผน:
                1. วิเคราะห์คำขอของผู้ใช้และระบุสถานที่หรือกิจกรรมใหม่ที่ต้องการเพิ่ม
                2. ตรวจสอบว่าสถานที่เหล่านั้นสามารถเพิ่มเข้าไปในแผนได้อย่างสมเหตุสมผลตามเส้นทางและตารางเวลา
                3. ปรับตารางเวลาและกิจกรรมที่มีอยู่เพื่อรองรับสถานที่หรือกิจกรรมใหม่
                4. ตรวจสอบว่าการเดินทางระหว่างสถานที่ยังคงเป็นไปได้หลังจากการปรับแผน
                5. คำนวณเวลาที่ต้องใช้ในแต่ละสถานที่ใหม่อย่างสมเหตุสมผล
                6. ปรับปรุงข้อมูลค่าใช้จ่ายถ้าจำเป็น
                
                สิ่งที่สำคัญที่สุด:
                - ต้องส่งกลับแผนการเดินทางฉบับสมบูรณ์ทั้งหมด ไม่ใช่เพียงส่วนที่มีการเปลี่ยนแปลง
                - รูปแบบของแผนต้องสอดคล้องกับแผนเดิม แต่ได้รับการปรับปรุงให้รวมสถานที่หรือกิจกรรมใหม่
                - อย่าตอบเพียงว่าได้เพิ่มอะไรเข้าไปในแผน แต่ต้องแสดงแผนทั้งหมดพร้อมการเปลี่ยนแปลงที่ทำ
                - แผนที่ปรับปรุงแล้วต้องมีความเป็นระเบียบเรียบร้อยและใช้งานได้จริง
                
                กรุณาตอบกลับด้วยแผนการเดินทางฉบับสมบูรณ์เท่านั้น ไม่ต้องอธิบายว่าคุณได้เปลี่ยนแปลงอะไร
                """

                logger.info(f"Preparing updated query for travel planner agent: {updated_query[:500]}...")
                
                # Tell the user we're updating the plan with more specific information
                yield {"message": "กำลังปรับปรุงแผนการเดินทางตามคำขอของคุณ โดยเพิ่มสถานที่ใหม่และปรับตารางเวลาให้เหมาะสม กรุณารอสักครู่...", "partial": True}
                
                logger.info(f"Updated query for plan update: {updated_query[:500]}...")
                
                # Save the updated query to a file for easier inspection
                try:
                    import os
                    from datetime import datetime
                    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
                    os.makedirs(log_dir, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    log_file = os.path.join(log_dir, f"updated_plan_query_{timestamp}.txt")
                    with open(log_file, "w", encoding="utf-8") as f:
                        f.write(f"SESSION ID: {session_id}\n\n")
                        f.write(f"USER REQUEST: {user_message}\n\n")
                        f.write(f"UPDATED QUERY:\n{updated_query}\n")
                    logger.info(f"Updated plan query saved to file: {log_file}")
                except Exception as e:
                    logger.error(f"Failed to save updated plan query to file: {e}")
                
                # Call travel planner agent with updated query
                yield {"message": "กำลังประมวลผลและปรับปรุงแผนการเดินทางให้รวมสถานที่เพิ่มเติมตามที่คุณต้องการ...", "partial": True}
                updated_travel_plan = call_sub_agent("travel_planner", updated_query, session_id)
                
                # Ensure the updated plan has the proper format
                if updated_travel_plan and "===== แผนการเดินทางของคุณ =====" not in updated_travel_plan:
                    updated_travel_plan = "===== แผนการเดินทางของคุณ (ฉบับปรับปรุง) =====\n\n" + updated_travel_plan
                
                # Store the updated plan in state manager
                state_manager.store_state(session_id, "last_travel_plan", updated_travel_plan)
                
                # Log the updated plan
                logger.info(f"Updated travel plan generated: {updated_travel_plan[:500]}...")
                
                # Save the updated plan to a file for easier inspection
                try:
                    import os
                    from datetime import datetime
                    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
                    os.makedirs(log_dir, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    log_file = os.path.join(log_dir, f"updated_travel_plan_{timestamp}.txt")
                    with open(log_file, "w", encoding="utf-8") as f:
                        f.write(f"SESSION ID: {session_id}\n\n")
                        f.write(f"USER REQUEST: {user_message}\n\n")
                        f.write(f"UPDATED TRAVEL PLAN:\n{updated_travel_plan}\n")
                    logger.info(f"Updated travel plan saved to file: {log_file}")
                except Exception as e:
                    logger.error(f"Failed to save updated travel plan to file: {e}")
                
                # Validate the updated plan has all necessary components before sending
                logger.info("Validating and sending updated travel plan to user")
                
                # Check if the updated plan seems to be missing content
                if len(updated_travel_plan.strip()) < 100:  # Simple validation for obviously incomplete plans
                    logger.warning("Updated travel plan seems too short, may be incomplete")
                    
                    # Try again with a more explicit instruction
                    retry_query = f"""
                    {updated_query}

                    *** สำคัญมาก ***
                    คุณต้องส่งแผนการเดินทางฉบับสมบูรณ์กลับมาทั้งหมด ไม่ใช่แค่ส่วนที่มีการเปลี่ยนแปลง
                    แผนทั้งหมดประกอบด้วย: ภาพรวม, การเดินทาง, ที่พัก, แผนรายวัน, ร้านอาหาร, คำแนะนำ
                    """
                    
                    yield {"message": "กำลังปรับปรุงรายละเอียดแผนการเดินทางเพิ่มเติม...", "partial": True}
                    
                    # Try once more with the travel planner agent
                    updated_travel_plan = call_sub_agent("travel_planner", retry_query, session_id)
                
                
                # Final formatting check - ensure it has a proper header
                if not updated_travel_plan.strip().startswith("===="):
                    updated_travel_plan = "===== แผนการเดินทางของคุณ (ฉบับปรับปรุง) =====\n\n" + updated_travel_plan
                
                # Send the complete updated plan
                yield {"message": updated_travel_plan, "final": True}
                return
            
            # Call appropriate sub-agent for specialized queries
            # No search results to enhance query
            enhanced_query = user_message

            specialized_response = call_sub_agent(query_type, enhanced_query, session_id)

            # Ensure we have a complete response
            if specialized_response:
                logger.info(f"Specialized response from {query_type} agent received: {specialized_response[:100]}...")
                # Make sure the response is properly formatted if it's a travel plan
                if query_type == "travel_planner" and "===== แผนการเดินทางของคุณ =====" not in specialized_response:
                    specialized_response = "===== แผนการเดินทางของคุณ =====\n\n" + specialized_response
                
                # Store the travel plan for potential updates later
                if query_type == "travel_planner":
                    logger.info("Storing travel plan in state manager")
                    state_manager.store_state(session_id, "last_travel_plan", specialized_response)
                
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

        # No external search results to add to the prompt

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

def classify_query(query: str) -> str:
    """
    Classify the user query to determine which sub-agent to use

    Args:
        query: The user's query

    Returns:
        The type of sub-agent to use: "accommodation", "activity", "restaurant", "transportation", "travel_planner", "youtube_insight", "plan_update" or "general"
    """
    query_lower = query.lower()

    # Log the query to help with debugging
    logger.info(f"Classifying query: {query_lower}")

    # Check for plan update with improved pattern matching for Thai language
    plan_update_patterns = ["เพิ่มสถานที่", "ปรับแผน", "เปลี่ยนแผน", "แก้ไขแผน", "อัพเดตแผน", "อัปเดตแผน", 
                          "แก้แผน", "เพิ่มแผน", "ต้องการเพิ่ม", "อยากเพิ่ม", "เพิ่มที่", "ใส่เพิ่ม"]
    
    # More specific pattern matching to avoid false positives
    if any(word in query_lower for word in plan_update_patterns) or "เข้าไปในแผน" in query_lower or ("เพิ่ม" in query_lower and "แผน" in query_lower):
        logger.info("Query classified as plan update")
        return "plan_update"

    # Travel planning
    if "ช่วยวางแผนการเดินทางท่องเที่ยว" in query_lower or "แผนการเดินทาง" in query_lower:
        logger.info("Query classified as travel planning")
        return "travel_planner"

    # Accommodation
    if any(word in query_lower for word in ["ที่พัก", "โรงแรม", "รีสอร์ท", "โฮสเทล"]):
        logger.info("Query classified as accommodation")
        return "accommodation"

    # Activities
    if any(word in query_lower for word in ["ที่เที่ยว", "สถานที่ท่องเที่ยว", "กิจกรรม", "เที่ยวที่ไหนดี"]):
        logger.info("Query classified as activity")
        return "activity"

    # Restaurants
    if any(word in query_lower for word in ["ร้านอาหาร", "อาหาร", "ที่กิน", "ร้านอร่อย"]):
        logger.info("Query classified as restaurant")
        return "restaurant"

    # Transportation
    if any(word in query_lower for word in ["การเดินทาง", "รถ", "เครื่องบิน", "รถไฟ", "รถทัวร์"]):
        logger.info("Query classified as transportation")
        return "transportation"

    # YouTube Insights
    if any(word in query_lower for word in ["youtube", "วิดีโอ", "ยูทูป", "คลิป", "รีวิว", "vlog", "วล็อก"]):
        logger.info("Query classified as youtube_insight")
        return "youtube_insight"

    # Default to general
    logger.info("Query classified as general")
    return "general"
