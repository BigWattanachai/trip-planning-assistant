"""
Utility for calling sub-agents in both Vertex AI and direct API modes.
Implements session state management following Google ADK best practices.
"""
import os
import logging
import google.generativeai as genai
from typing import Any, Dict, Optional

from config import settings
from services.session import get_session_manager
from agent.tools.extract_info import extract_travel_info
from agent.tools.tavily_search import tavily_search

# Import sub-agents
try:
    from sub_agents import (
        AccommodationAgent, accommodation_tavily_search,
        ActivityAgent, activity_tavily_search,
        RestaurantAgent, restaurant_tavily_search,
        TransportationAgent, transportation_tavily_search,
        TravelPlannerAgent, travel_planner_tavily_search
    )
except ImportError as e:
    logger.warning(f"Could not import some sub-agents: {e}")
    # Set default values for missing imports
    AccommodationAgent = None
    accommodation_tavily_search = None
    ActivityAgent = None
    activity_tavily_search = None
    RestaurantAgent = None
    restaurant_tavily_search = None
    TransportationAgent = None
    transportation_tavily_search = None
    TravelPlannerAgent = None
    travel_planner_tavily_search = None

logger = logging.getLogger(__name__)

def call_sub_agent(
    agent_type: str,
    query: str,
    session_id: str = None,
    state: Dict[str, Any] = None
) -> str:
    """
    Calls a sub-agent with the given query, using either ADK or direct API.
    Implements session state management following Google ADK best practices.
    
    Args:
        agent_type: The type of sub-agent to call ("accommodation", "activity", 
                   "restaurant", "transportation", "travel_planner")
        query: The user query to process
        session_id: Optional session ID for state management
        state: Optional state dictionary to use instead of session state
        
    Returns:
        The sub-agent's response as a string
    """
    # Get session manager for state management
    session_manager = get_session_manager()
    
    # Initialize state from session if not provided
    if state is None and session_id:
        state = session_manager.get_all_state(session_id) or {}
    elif state is None:
        state = {}
    
    # Extract travel information from the query if not already in state
    if "destination" not in state:
        travel_info = extract_travel_info(query)
        # Update state with travel info
        state.update(travel_info)
        # Also store in session if session_id is provided
        if session_id:
            for key, value in travel_info.items():
                session_manager.store_state(session_id, key, value)
    
    # Check if we're using Vertex AI mode
    vertex_ai_mode = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes")
    
    # Try to use ADK agents if in Vertex AI mode
    if vertex_ai_mode:
        # Map agent_type to the corresponding ADK agent
        adk_agents = {
            "accommodation": AccommodationAgent,
            "activity": ActivityAgent,
            "restaurant": RestaurantAgent,
            "transportation": TransportationAgent,
            "travel_planner": TravelPlannerAgent
        }
        
        # Get the appropriate agent
        agent = adk_agents.get(agent_type)
        
        if agent:
            try:
                logger.info(f"Using ADK agent for {agent_type}")
                
                # Create tool context for state management
                tool_context = {
                    "state": state,
                    "session_id": session_id
                }
                
                # Call the agent with the query and tool context
                response = agent.generate_content(query, tool_context=tool_context)
                
                # Get the response text
                response_text = response.text
                
                # Store the response in session state if session_id is provided
                if session_id:
                    session_manager.store_state(session_id, f"{agent_type}_response", response_text)
                    
                    # For travel planner, also store as last_response for output_key compatibility
                    if agent_type == "travel_planner":
                        session_manager.store_state(session_id, "last_response", response_text)
                
                logger.info(f"ADK {agent_type} agent response: {response_text[:100]}...")
                return response_text
            except Exception as e:
                logger.error(f"Error using ADK {agent_type} agent: {e}")
                # Fall back to direct API mode
                logger.info(f"Falling back to direct API mode for {agent_type}")
    
    # If we're here, we're using direct API mode or ADK mode failed
    
    # Get API key from environment
    api_key = settings.GOOGLE_API_KEY
    if not api_key:
        logger.error("GOOGLE_API_KEY not set. Cannot call sub-agent.")
        return "Error: GOOGLE_API_KEY not set."
    
    # Configure the Gemini API
    genai.configure(api_key=api_key)
    
    # Get the model to use
    model = genai.GenerativeModel(settings.MODEL)
    
    # Prepare search results for each agent type
    search_info = ""
    destination = state.get('destination', '')
    origin = state.get('origin', '')
    
    # Only perform searches if Tavily API key is available and destination is specified
    if settings.TAVILY_API_KEY and destination and destination not in ["ไม่ระบุ", "ภายในประเทศไทย"]:
        try:
            logger.info(f"Using Tavily search for {agent_type} agent with destination: {destination}")
            
            # Define search queries based on agent type
            search_queries = []
            
            if agent_type == "accommodation":
                search_queries = [
                    f"ที่พักยอดนิยมใน {destination} 2025",
                    f"โรงแรมราคาประหยัดใน {destination}",
                    f"รีสอร์ทและโรงแรมบูติคใน {destination}",
                    f"โฮสเทลและเกสต์เฮาส์ใน {destination}"
                ]
                
                # Use the accommodation_tavily_search function if available
                search_function = accommodation_tavily_search if accommodation_tavily_search else tavily_search
                
            elif agent_type == "activity":
                search_queries = [
                    f"สถานที่ท่องเที่ยวยอดนิยมใน {destination} 2025",
                    f"กิจกรรมทางวัฒนธรรมที่น่าสนใจใน {destination}",
                    f"กิจกรรมท่องเที่ยวธรรมชาติและกลางแจ้งใน {destination}",
                    f"ประสบการณ์ท้องถิ่นที่ไม่เหมือนใครใน {destination}"
                ]
                
                # Use the activity_tavily_search function if available
                search_function = activity_tavily_search if activity_tavily_search else tavily_search
                
            elif agent_type == "restaurant":
                search_queries = [
                    f"ร้านอาหารยอดนิยมใน {destination} 2025",
                    f"อาหารท้องถิ่นที่ต้องลองใน {destination}",
                    f"ร้านอาหารราคาประหยัดใน {destination}",
                    f"ร้านอาหารระดับพรีเมียมใน {destination}"
                ]
                
                # Use the restaurant_tavily_search function if available
                search_function = restaurant_tavily_search if restaurant_tavily_search else tavily_search
                
            elif agent_type == "transportation":
                search_queries = [
                    f"วิธีเดินทางจาก {origin} ไป {destination}",
                    f"ขนส่งสาธารณะใน {destination}",
                    f"บริการเช่ารถและรถจักรยานยนต์ใน {destination}",
                    f"ค่าโดยสารและตารางเวลาเดินทางไป {destination}"
                ]
                
                # Use the transportation_tavily_search function if available
                search_function = transportation_tavily_search if transportation_tavily_search else tavily_search
                
            elif agent_type == "travel_planner":
                search_queries = [
                    f"แผนการท่องเที่ยว {destination} 3 วัน",
                    f"สถานที่ท่องเที่ยวยอดนิยมใน {destination}",
                    f"ที่พักและร้านอาหารแนะนำใน {destination}",
                    f"เคล็ดลับการท่องเที่ยว {destination} 2025"
                ]
                
                # Use the travel_planner_tavily_search function if available
                search_function = travel_planner_tavily_search if travel_planner_tavily_search else tavily_search
            
            # Perform searches for the queries
            search_results = {}
            for search_query in search_queries:
                logger.info(f"Searching Tavily for {agent_type}: {search_query}")
                result = search_function(search_query)
                if result:
                    category = search_query.split(" in ")[0] if " in " in search_query else search_query
                    search_results[category] = result
                    logger.info(f"Got Tavily results for {agent_type}: {category}")
            
            # Append search results to query for the model
            if search_results:
                search_info = "\n\nAdditional information from real-time search:\n"
                for category, result in search_results.items():
                    summary = str(result)[:1000]  # Truncate long results
                    search_info += f"\n--- {category} ---\n{summary}\n"
                
                logger.info(f"Adding Tavily search results to {agent_type} prompt")
                
                # Store in session state if session_id is provided
                if session_id:
                    session_manager.store_state(session_id, f"{agent_type}_search_results", search_results)
            else:
                search_info = "\n\nNote: Attempted to search for additional information, but no results were found."
        except Exception as e:
            logger.error(f"Error using Tavily search for {agent_type}: {e}")
            search_info = "\n\nNote: Attempted to search for additional information, but encountered an error."
    
    # Create specialized queries for different sub-agents
    specialized_queries = {
        "accommodation": f"""
            ฉันกำลังวางแผนเดินทางจาก {state.get('origin', 'กรุงเทพ')} ไป {state.get('destination', 'ภายในประเทศไทย')} 
            ในวันที่ {state.get('start_date', 'ไม่ระบุ')} ถึง {state.get('end_date', 'ไม่ระบุ')}
            มีงบประมาณทั้งหมด {state.get('budget', 'ไม่ระบุ')} บาท
            
            ช่วยแนะนำที่พักที่เหมาะสมได้ไหม? ต้องการที่พักคุณภาพดี ราคาคุ้มค่า ทำเลสะดวก
            พร้อมราคาต่อคืนที่เหมาะกับงบประมาณ
        """,
        
        "activity": f"""
            ฉันกำลังวางแผนเดินทางไป {state.get('destination', 'ภายในประเทศไทย')} 
            ในวันที่ {state.get('start_date', 'ไม่ระบุ')} ถึง {state.get('end_date', 'ไม่ระบุ')}
            มีงบประมาณทั้งหมด {state.get('budget', 'ไม่ระบุ')} บาท
            
            ช่วยแนะนำสถานที่ท่องเที่ยวสำคัญและกิจกรรมที่น่าสนใจได้ไหม?
            ต้องการเน้นสถานที่สำคัญทางวัฒนธรรม ธรรมชาติ และจุดถ่ายรูปยอดนิยม{search_info}
        """,
        
        "restaurant": f"""
            ฉันกำลังวางแผนเดินทางไป {state.get('destination', 'ภายในประเทศไทย')} 
            ในวันที่ {state.get('start_date', 'ไม่ระบุ')} ถึง {state.get('end_date', 'ไม่ระบุ')}
            มีงบประมาณทั้งหมด {state.get('budget', 'ไม่ระบุ')} บาท
            
            ช่วยแนะนำร้านอาหารอร่อยที่ {state.get('destination', 'ภายในประเทศไทย')} ได้ไหม? 
            ต้องการทราบชื่อร้าน ประเภทอาหาร เมนูเด็ดที่ต้องลอง และราคาคร่าวๆ ต่อมื้อ
            อยากได้หลากหลายราคาทั้งแบบประหยัดและร้านดังๆ
        """,
        
        "transportation": f"""
            ฉันกำลังวางแผนเดินทางจาก {state.get('origin', 'กรุงเทพ')} ไป {state.get('destination', 'ภายในประเทศไทย')} 
            ในวันที่ {state.get('start_date', 'ไม่ระบุ')} และกลับในวันที่ {state.get('end_date', 'ไม่ระบุ')}
            มีงบประมาณทั้งหมด {state.get('budget', 'ไม่ระบุ')} บาท
            
            ช่วยแนะนำวิธีการเดินทางไป-กลับระหว่าง {state.get('origin', 'กรุงเทพ')} และ {state.get('destination', 'ภายในประเทศไทย')} ได้ไหม? 
            ต้องการทราบตัวเลือกการเดินทาง เช่น รถยนต์ เครื่องบิน รถทัวร์ พร้อมเวลาเดินทางและราคาค่าโดยสาร
            รวมทั้งวิธีเดินทางในพื้นที่ {state.get('destination', 'ภายในประเทศไทย')}
        """,
        
        "travel_planner": query  # Travel planner gets the full query
    }
    
    # Define prompts for different sub-agents
    prompts = {
        "accommodation": f"""คุณคือผู้เชี่ยวชาญด้านที่พัก ให้คำแนะนำที่พักที่เหมาะสมกับความต้องการของผู้ใช้
คำขอ: {specialized_queries.get(agent_type, query)}

โปรดให้คำแนะนำเกี่ยวกับ:
1. ประเภทที่พัก (โรงแรม, โฮสเทล, รีสอร์ท, เกสต์เฮาส์) ที่ {state.get('destination', 'ภายในประเทศไทย')}
2. ช่วงราคาโดยประมาณต่อคืน (บาท)
3. ย่านหรือพื้นที่ที่เหมาะสม ใกล้สถานที่ท่องเที่ยว
4. สิ่งอำนวยความสะดวกที่ตรงกับความต้องการของผู้ใช้
5. ข้อพิจารณาพิเศษตามบริบทการเดินทาง

แนะนำที่พักอย่างน้อย 3-5 แห่ง พร้อมราคาและจุดเด่น โดยเลือกให้เหมาะกับงบประมาณ 
ให้คำแนะนำที่กระชับแต่มีข้อมูลครบถ้วน โดยมุ่งเน้นตัวเลือกที่เหมาะกับความต้องการและความชอบของผู้ใช้มากที่สุด{search_info}""",
        
        "activity": f"""คุณคือผู้เชี่ยวชาญด้านกิจกรรมและสถานที่ท่องเที่ยว ให้คำแนะนำเกี่ยวกับกิจกรรมที่น่าสนใจตามความต้องการของผู้ใช้
คำขอ: {specialized_queries.get(agent_type, query)}

โปรดให้คำแนะนำเกี่ยวกับกิจกรรมและสถานที่ท่องเที่ยวที่ {state.get('destination', 'ภายในประเทศไทย')} โดยครอบคลุม:
1. สถานที่ท่องเที่ยวยอดนิยมที่ไม่ควรพลาด 5-10 แห่ง
2. กิจกรรมทางวัฒนธรรม (พิพิธภัณฑ์, วัด, สถานที่ประวัติศาสตร์)
3. กิจกรรมกลางแจ้งและธรรมชาติ
4. ประสบการณ์ท้องถิ่นที่ไม่ใช่ที่ท่องเที่ยวกระแสหลัก
5. ค่าเข้าชมหรือค่าธรรมเนียมโดยประมาณ (บาท)
6. เวลาที่ใช้สำหรับแต่ละกิจกรรม

จัดเรียงกิจกรรมตามความสำคัญ และแนะนำแผนการท่องเที่ยวที่เหมาะสมสำหรับระยะเวลา {state.get('start_date', 'ไม่ระบุ')} ถึง {state.get('end_date', 'ไม่ระบุ')}
ให้คำแนะนำที่กระชับแต่มีข้อมูลครบถ้วน โดยมุ่งเน้นตัวเลือกที่น่าสนใจและเหมาะกับงบประมาณ {state.get('budget', 'ไม่ระบุ')} บาท{search_info}""",
        
        "restaurant": f"""คุณคือผู้เชี่ยวชาญด้านอาหารและร้านอาหาร ให้คำแนะนำร้านอาหารตามความต้องการของผู้ใช้
คำขอ: {specialized_queries.get(agent_type, query)}

โปรดให้คำแนะนำเกี่ยวกับร้านอาหารที่ {state.get('destination', 'ภายในประเทศไทย')} โดยครอบคลุม:
1. อาหารท้องถิ่นที่ห้ามพลาดและร้านที่ขึ้นชื่อ
2. ร้านอาหารยอดนิยมสำหรับมื้อต่างๆ (อาหารเช้า, กลางวัน, เย็น)
3. ร้านอาหารในหลายระดับราคา (ประหยัด ปานกลาง หรูหรา)
4. ตลาดอาหารหรือตัวเลือกอาหารริมทาง
5. เมนูแนะนำและราคาโดยประมาณต่อมื้อ (บาท)

แนะนำร้านอาหารอย่างน้อย 8-10 ร้าน ที่มีความหลากหลายทั้งประเภทอาหารและราคา เน้นร้านที่มีชื่อเสียงและอาหารท้องถิ่น
ให้คำแนะนำที่กระชับแต่มีข้อมูลครบถ้วน ระบุทำเลที่ตั้งของร้านโดยคร่าวๆ เพื่อให้ผู้ใช้เดินทางได้สะดวก{search_info}""",
        
        "transportation": f"""คุณคือผู้เชี่ยวชาญด้านการเดินทาง ให้คำแนะนำเกี่ยวกับการเดินทางตามความต้องการของผู้ใช้
คำขอ: {specialized_queries.get(agent_type, query)}

โปรดให้คำแนะนำเกี่ยวกับ:
1. วิธีเดินทางระหว่าง {state.get('origin', 'กรุงเทพ')} และ {state.get('destination', 'ภายในประเทศไทย')} โดยละเอียด
   • ตัวเลือกการเดินทาง (เครื่องบิน, รถไฟ, รถโดยสาร, เรือ)
   • สายการบินหรือบริษัทขนส่งที่ให้บริการ
   • เวลาเดินทางโดยประมาณ
   • ราคาค่าโดยสารโดยประมาณสำหรับแต่ละตัวเลือก (บาท)
   • ความถี่ของเที่ยวบินหรือเที่ยวรถ

2. การเดินทางในพื้นที่ {state.get('destination', 'ภายในประเทศไทย')}
   • ระบบขนส่งสาธารณะ
   • แท็กซี่และบริการเรียกรถ
   • บริการเช่ายานพาหนะ (รถยนต์, จักรยานยนต์)
   • ค่าใช้จ่ายโดยประมาณของแต่ละวิธี

3. คำแนะนำพิเศษ
   • เส้นทางที่ดีที่สุดสำหรับการเดินทาง
   • การจองตั๋วล่วงหน้า
   • เคล็ดลับประหยัดค่าเดินทาง

ให้คำแนะนำที่กระชับแต่มีข้อมูลครบถ้วน เน้นตัวเลือกที่สะดวก ปลอดภัย และเหมาะกับงบประมาณ {state.get('budget', 'ไม่ระบุ')} บาท{search_info}""",
        
        "travel_planner": f"""คุณคือผู้วางแผนการเดินทางผู้เชี่ยวชาญ สร้างแผนการเดินทางแบบครบวงจร
คำขอ: {query}

หลังจากวิเคราะห์คำขอของผู้ใช้ โปรดสร้างแผนการเดินทางจาก {state.get('origin', 'กรุงเทพ')} ไป {state.get('destination', 'ภายในประเทศไทย')} 
ในวันที่ {state.get('start_date', 'ไม่ระบุ')} ถึง {state.get('end_date', 'ไม่ระบุ')} โดยมีงบประมาณ {state.get('budget', 'ไม่ระบุ')} บาท

แผนการเดินทางต้องครอบคลุม:
1. การเดินทางไป-กลับ ระหว่าง {state.get('origin', 'กรุงเทพ')} และ {state.get('destination', 'ภายในประเทศไทย')} 
   (เลือกวิธีที่ดีที่สุดทั้งด้านราคาและความสะดวก)
2. ที่พักตลอดการเดินทาง (เลือกที่พักที่เหมาะสมกับงบประมาณ แต่มีคุณภาพดี)
3. สถานที่ท่องเที่ยวและกิจกรรมในแต่ละวัน จัดเรียงตามความสำคัญและตำแหน่งที่ตั้ง
4. ร้านอาหารแนะนำสำหรับแต่ละวัน
5. การเดินทางในพื้นที่ระหว่างสถานที่ท่องเที่ยว
6. แผนสำรองในกรณีที่มีปัญหา (สภาพอากาศไม่ดี, สถานที่ปิด)
7. ค่าใช้จ่ายโดยละเอียดในแต่ละวัน แยกตามหมวดหมู่ (ที่พัก, อาหาร, เดินทาง, กิจกรรม)
8. คำแนะนำและข้อควรระวังเพื่อความปลอดภัยและประทับใจ

จัดทำตารางเวลาแบบวันต่อวันที่ชัดเจน คำนวณค่าใช้จ่ายรวมให้ไม่เกินงบประมาณ {state.get('budget', 'ไม่ระบุ')} บาท
กรุณาจัดรูปแบบด้วยหัวข้อ "===== แผนการเดินทางของคุณ =====" และใช้การจัดรูปแบบที่อ่านง่าย{search_info}
"""
    }
    
    # Determine which sub-agent to use based on the type
    if agent_type in prompts:
        prompt = prompts[agent_type]
    else:
        # Default to travel planner if agent type not recognized
        logger.warning(f"Unknown agent type: {agent_type}, using travel_planner")
        prompt = prompts["travel_planner"]
    
    logger.info(f"Calling sub-agent: {agent_type}")
    
    try:
        # Generate the response
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            },
        )
        
        # Get the response text
        response_text = response.text
        
        # Store the response in session state if session_id is provided
        if session_id:
            session_manager.store_state(session_id, f"{agent_type}_response", response_text)
            
            # For travel planner, also store as last_response for output_key compatibility
            if agent_type == "travel_planner":
                session_manager.store_state(session_id, "last_response", response_text)
        
        logger.info(f"Sub-agent {agent_type} response: {response_text[:100]}...")
        return response_text
    except Exception as e:
        logger.error(f"Error calling sub-agent {agent_type}: {e}")
        return f"Error: {str(e)}"
