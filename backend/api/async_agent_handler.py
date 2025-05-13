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

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Add the parent directory to sys.path to allow imports
parent_dir = str(pathlib.Path(__file__).parent.parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Add the current directory's parent to sys.path
current_parent = str(pathlib.Path(__file__).parent.parent.absolute())
if current_parent not in sys.path:
    sys.path.append(current_parent)

# Add current directory to sys.path
current_dir = str(pathlib.Path(__file__).parent.absolute())
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import common modules
try:
    # Try with backend-improve prefix first
    try:
        from backend_improve.tools.tavily_search import search_with_tavily, format_tavily_results_for_agent
        TAVILY_AVAILABLE = True
        logger.info("Successfully imported Tavily search functions with backend_improve prefix")
    except ImportError:
        # Try direct import
        from tools.tavily_search import search_with_tavily, format_tavily_results_for_agent
        TAVILY_AVAILABLE = True
        logger.info("Successfully imported Tavily search functions with direct import")
except ImportError as e:
    logger.warning(f"Could not import Tavily search function: {e}")
    TAVILY_AVAILABLE = False

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
        root_agent = None
        try:
            # Try with backend-improve prefix first
            from backend_improve.agent import root_agent
            logger.info("Successfully imported root_agent from backend_improve.agent module")
        except ImportError:
            # Try direct import
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
        # Try to import from backend_improve.agent first
        try:
            from backend_improve.agent import call_sub_agent, extract_travel_info
            logger.info("Successfully imported call_sub_agent from backend_improve.agent")
        except ImportError:
            # If that fails, try from agent
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
                # Ensure ADK session exists before processing
                try:
                    adk_app.create_session(user_id=user_id, session_id=session_id)
                    logger.info(f"Created ADK session for user_id={user_id}, session_id={session_id}")
                except Exception as create_err:
                    logger.info(f"ADK session may already exist or failed to create: {create_err}")
                
                # Process the message through ADK app
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

                # Search for destination information if Tavily is available
                destination_info = ""
                if TAVILY_AVAILABLE and destination and destination != "ไม่ระบุ" and destination != "ภายในประเทศไทย":
                    try:
                        logger.info(f"Searching for information about {destination}")
                        yield {"message": f"กำลังค้นหาข้อมูลเกี่ยวกับ {destination}...", "partial": True}
                        
                        # Search for travel information
                        search_results = search_with_tavily(
                            query=f"travel guide tourist information {destination} 2025",
                            location=destination,
                            max_results=5
                        )
                        
                        if search_results and search_results.get("success", False):
                            destination_info = format_tavily_results_for_agent(search_results)
                            logger.info(f"Found destination information: {len(destination_info)} characters")
                        else:
                            logger.warning("No search results found for the destination")
                    except Exception as e:
                        logger.error(f"Error searching for destination information: {e}")

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
                
                # Call our new YouTube insight agent
                logger.info("Calling YouTube insight sub-agent")
                youtube_insight_response = call_sub_agent("youtube_insight", user_message, session_id)
                yield {"message": "กำลังวิเคราะห์ข้อมูลจากวิดีโอ YouTube เกี่ยวกับจุดหมายปลายทาง...", "partial": True}

                # Finally, call the travel planner to create a comprehensive plan
                logger.info("Calling travel planner sub-agent")
                # Include info from other sub-agents in the travel planner's input
                enhanced_query = f"""
                {user_message}

                ข้อมูลจากการค้นหา:
                {destination_info[:1000] if destination_info else "ไม่มีข้อมูลจากการค้นหา"}

                ข้อมูลการเดินทาง:
                {transportation_response[:1000] if transportation_response else "ไม่มีข้อมูล"}

                ข้อมูลที่พัก:
                {accommodation_response[:1000] if accommodation_response else "ไม่มีข้อมูล"}

                ข้อมูลร้านอาหาร:
                {restaurant_response[:1000] if restaurant_response else "ไม่มีข้อมูล"}

                ข้อมูลสถานที่ท่องเที่ยวและกิจกรรม:
                {activity_response[:1000] if activity_response else "ไม่มีข้อมูล"}
                
                ข้อมูลเชิงลึกจาก YouTube:
                {youtube_insight_response[:1000] if youtube_insight_response else "ไม่มีข้อมูล"}
                """

                # Log the enhanced query for debugging
                logger.info(f"Enhanced query for travel planner: {enhanced_query[:5000]}...")

                yield {"message": "กำลังจัดทำแผนการเดินทางแบบสมบูรณ์...", "partial": True}

                travel_plan = call_sub_agent("travel_planner", enhanced_query, session_id)

                # Ensure the travel plan has the proper format
                if travel_plan and "===== แผนการเดินทางของคุณ =====" not in travel_plan:
                    travel_plan = "===== แผนการเดินทางของคุณ =====\n\n" + travel_plan

                # Log the complete travel plan
                logger.info(f"Travel plan created: {travel_plan[:100]}...")

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

        # Search for relevant information if Tavily is available
        search_results = None
        if TAVILY_AVAILABLE and query_type != "general":
            try:
                # Extract relevant information for search
                travel_info = extract_travel_info(user_message)
                destination = travel_info.get("destination", "")
                
                if destination and destination != "ไม่ระบุ" and destination != "ภายในประเทศไทย":
                    logger.info(f"Searching for information about {destination} related to {query_type}")
                    yield {"message": f"กำลังค้นหาข้อมูลที่เกี่ยวข้อง...", "partial": True}
                    
                    # Map query types to search query templates
                    search_queries = {
                        "accommodation": f"best hotels and accommodation in {destination} 2025",
                        "activity": f"top tourist attractions and activities in {destination} 2025",
                        "restaurant": f"best restaurants and local cuisine in {destination}",
                        "transportation": f"transportation options and how to get to {destination}",
                        "travel_planner": f"travel guide tourist information {destination} 2025"
                    }
                    
                    # Get the appropriate search query
                    search_query = search_queries.get(query_type, f"{destination} tourist information")
                    
                    # Execute search
                    search_results = search_with_tavily(search_query, destination)
                    
                    if search_results and search_results.get("success", False):
                        logger.info(f"Found relevant information for {query_type}")
                    else:
                        logger.warning(f"No search results found for {destination} related to {query_type}")
            except Exception as e:
                logger.error(f"Error searching for relevant information: {e}")

        if query_type != "general":
            # Call appropriate sub-agent for specialized queries
            
            # Enhance query with search results if available
            enhanced_query = user_message
            if search_results and search_results.get("success", False):
                formatted_results = format_tavily_results_for_agent(search_results)
                enhanced_query += f"\n\nข้อมูลจากการค้นหาล่าสุด:\n{formatted_results}"
                logger.info("Added search results to query")
            
            specialized_response = call_sub_agent(query_type, enhanced_query, session_id)

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

        # If Tavily information is available, add it to the prompt
        if search_results and search_results.get("success", False):
            formatted_results = format_tavily_results_for_agent(search_results)
            prompt += f"\n\nข้อมูลจากการค้นหาล่าสุด:\n{formatted_results}"
            logger.info("Added search results to general prompt")

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
        The type of sub-agent to use: "accommodation", "activity", "restaurant", "transportation", "travel_planner", "youtube_insight", or "general"
    """
    query_lower = query.lower()

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
