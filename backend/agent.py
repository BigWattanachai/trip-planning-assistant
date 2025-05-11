"""Travel Agent using Google ADK."""

import os
import logging
import sys
import pathlib
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to sys.path
parent_dir = str(pathlib.Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Tavily search function from activity agent
try:
    from sub_agents.activity_agent import activity_tavily_search
    TAVILY_AVAILABLE = activity_tavily_search is not None
    if TAVILY_AVAILABLE:
        logger.info("Successfully imported Tavily search function")
        print("Successfully imported Tavily search function")
    else:
        logger.warning("Tavily search function is not available")
        print("Tavily search function is not available")
except ImportError as e:
    logger.warning(f"Could not import Tavily search function: {e}")
    print(f"Could not import Tavily search function: {e}")
    TAVILY_AVAILABLE = False

# Only import ADK components if we're using Vertex AI
if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes"):
    try:
        import warnings
        from google.adk.agents import Agent
        from google.adk.tools import ToolContext
        
        warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")
        
        MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")
        logger.info(f"ADK Mode: Using model {MODEL}")
        
        # Simple tool to store state
        def store_state_tool(state: dict, tool_context: ToolContext) -> dict:
            """Stores new state values in the ToolContext."""
            logger.info(f"Storing state: {state}")
            tool_context.state.update(state)
            return {"status": "ok"}
        
        store_state_tool.description = "Store state values in the ToolContext."
        
        # Import sub-agents
        try:
            # Try direct import first
            from sub_agents import (
                AccommodationAgent,
                ActivityAgent,
                RestaurantAgent,
                TransportationAgent,
                TravelPlannerAgent
            )
            logger.info("Successfully imported sub-agents using direct path")
        except ImportError:
            # Try with backend prefix
            from backend.sub_agents import (
                AccommodationAgent,
                ActivityAgent,
                RestaurantAgent,
                TransportationAgent,
                TravelPlannerAgent
            )
            logger.info("Successfully imported sub-agents using backend path")
        
        # Import the root agent prompt
        try:
            # Try direct import first
            from root_agent_prompt import PROMPT as ROOT_PROMPT
        except ImportError:
            # Try with backend prefix
            from backend.root_agent_prompt import PROMPT as ROOT_PROMPT
        
        # Create the root agent with all sub-agents
        root_agent = Agent(
            model=MODEL,
            name="root_agent",
            description="Travel planning agent that creates comprehensive travel plans",
            instruction=ROOT_PROMPT,
            tools=[store_state_tool],
            sub_agents=[
                AccommodationAgent,
                ActivityAgent,
                RestaurantAgent,
                TransportationAgent,
                TravelPlannerAgent
            ],
        )
        logger.info("Root agent created with all sub-agents")
        
    except ImportError as e:
        logger.warning(f"Failed to import ADK components: {e}")
        root_agent = None
else:
    logger.info("Direct API Mode: ADK components not loaded")
    root_agent = None

def extract_travel_info(query):
    """
    Extract travel information from the query
    
    Args:
        query: The user query
        
    Returns:
        Dictionary with extracted travel info
    """
    # Initialize default values
    travel_info = {
        "origin": "กรุงเทพ",  # Default origin
        "destination": "ภายในประเทศไทย",  # Default destination
        "start_date": "ไม่ระบุ",
        "end_date": "ไม่ระบุ",
        "budget": "ไม่ระบุ",
        "num_travelers": 1,
        "preferences": []
    }
    
    # Extract origin
    origin_match = re.search(r"ต้นทาง:\s*([^\n]+)", query)
    if origin_match:
        travel_info["origin"] = origin_match.group(1).strip()
    
    # Extract destination
    destination_match = re.search(r"ปลายทาง:\s*([^\n]+)", query)
    if destination_match:
        travel_info["destination"] = destination_match.group(1).strip()
    
    # Extract dates
    dates_match = re.search(r"ช่วงเวลาเดินทาง:.*?วันที่:\s*(\d{4}-\d{2}-\d{2})(?:\s*ถึงวันที่\s*(\d{4}-\d{2}-\d{2}))?", query)
    if dates_match:
        travel_info["start_date"] = dates_match.group(1).strip()
        if dates_match.group(2):
            travel_info["end_date"] = dates_match.group(2).strip()
        else:
            travel_info["end_date"] = travel_info["start_date"]  # Same day trip
    
    # Extract budget
    budget_match = re.search(r"งบประมาณรวม:\s*ไม่เกิน\s*(\d+,?\d*)\s*บาท", query)
    if budget_match:
        travel_info["budget"] = budget_match.group(1).strip()
    
    return travel_info

# Define a function to simulate sub-agent calls in direct API mode
def call_sub_agent(agent_type, query, session_id=None):
    """
    Simulates calling a sub-agent in direct API mode with specialized prompts
    
    Args:
        agent_type: The type of sub-agent to call ("accommodation", "activity", "restaurant", "transportation", "travel_planner")
        query: The user query to process
        session_id: Optional session ID
        
    Returns:
        The sub-agent's response
    """
    import google.generativeai as genai
    
    # Get the API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not set. Cannot call sub-agent.")
        return "Error: GOOGLE_API_KEY not set."
    
    # Configure the Gemini API
    genai.configure(api_key=api_key)
    
    # Get the model to use
    model_name = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")
    model = genai.GenerativeModel(model_name)
    
    # Extract travel information from the query
    travel_info = extract_travel_info(query)
    logger.info(f"Extracted travel info: {travel_info}")
    
    # Special handling for activity agent when Tavily is available
    if agent_type == "activity" and TAVILY_AVAILABLE:
        try:
            # Use Tavily search to enhance results
            logger.info("Using Tavily search to enhance activity recommendations")
            print("Using Tavily search to enhance activity recommendations")
            
            destination = travel_info['destination']
            # Perform searches for different categories of activities
            search_queries = [
                f"สถานที่ท่องเที่ยวยอดนิยมใน  {destination} 2025",
                f"กิจกรรมทางวัฒนธรรมที่น่าสนใจใน {destination}",
                f"กิจกรรมท่องเที่ยวธรรมชาติและกลางแจ้งใน  {destination}",
                f"ประสบการณ์ท้องถิ่นที่ไม่เหมือนใครใน  {destination}",
            ]
            
            search_results = {}
            for search_query in search_queries:
                logger.info(f"Searching Tavily for: {search_query}")
                result = activity_tavily_search(search_query)
                if result:
                    category = search_query.split(" in ")[0]
                    search_results[category] = result
                    logger.info(f"Got Tavily results for: {category}")
            
            # Append search results to query for the model
            if search_results:
                activity_info = "\n\nAdditional information from real-time search:\n"
                for category, result in search_results.items():
                    summary = str(result)[:1000]  # Truncate long results
                    activity_info += f"\n--- {category} ---\n{summary}\n"
                
                logger.info("Adding Tavily search results to prompt")
            else:
                activity_info = "\n\nNote: Attempted to search for additional information, but no results were found."
        except Exception as e:
            logger.error(f"Error using Tavily search: {e}")
            activity_info = "\n\nNote: Attempted to search for additional information, but encountered an error."
    else:
        activity_info = ""
    
    # Create specialized queries for different sub-agents
    specialized_queries = {
        "accommodation": f"""
            ฉันกำลังวางแผนเดินทางจาก {travel_info['origin']} ไป {travel_info['destination']} 
            ในวันที่ {travel_info['start_date']} ถึง {travel_info['end_date']}
            มีงบประมาณทั้งหมด {travel_info['budget']} บาท
            
            ช่วยแนะนำที่พักที่เหมาะสมได้ไหม? ต้องการที่พักคุณภาพดี ราคาคุ้มค่า ทำเลสะดวก
            พร้อมราคาต่อคืนที่เหมาะกับงบประมาณ
        """,
        
        "activity": f"""
            ฉันกำลังวางแผนเดินทางไป {travel_info['destination']} 
            ในวันที่ {travel_info['start_date']} ถึง {travel_info['end_date']}
            มีงบประมาณทั้งหมด {travel_info['budget']} บาท
            
            ช่วยแนะนำสถานที่ท่องเที่ยวสำคัญและกิจกรรมที่น่าสนใจได้ไหม?
            ต้องการเน้นสถานที่สำคัญทางวัฒนธรรม ธรรมชาติ และจุดถ่ายรูปยอดนิยม
        """,
        
        "restaurant": f"""
            ฉันกำลังวางแผนเดินทางไป {travel_info['destination']} 
            ในวันที่ {travel_info['start_date']} ถึง {travel_info['end_date']}
            มีงบประมาณทั้งหมด {travel_info['budget']} บาท
            
            ช่วยแนะนำร้านอาหารอร่อยที่ {travel_info['destination']} ได้ไหม? 
            ต้องการทราบชื่อร้าน ประเภทอาหาร เมนูเด็ดที่ต้องลอง และราคาคร่าวๆ ต่อมื้อ
            อยากได้หลากหลายราคาทั้งแบบประหยัดและร้านดังๆ
        """,
        
        "transportation": f"""
            ฉันกำลังวางแผนเดินทางจาก {travel_info['origin']} ไป {travel_info['destination']} 
            ในวันที่ {travel_info['start_date']} และกลับในวันที่ {travel_info['end_date']}
            มีงบประมาณทั้งหมด {travel_info['budget']} บาท
            
            ช่วยแนะนำวิธีการเดินทางไป-กลับระหว่าง {travel_info['origin']} และ {travel_info['destination']} ได้ไหม? 
            ต้องการทราบตัวเลือกการเดินทาง เช่น รถยนต์ เครื่องบิน รถทัวร์ พร้อมเวลาเดินทางและราคาค่าโดยสาร
            รวมทั้งวิธีเดินทางในพื้นที่ {travel_info['destination']}
        """,
        
        "travel_planner": query  # Travel planner still gets the full query
    }
    
    # Define prompts for different sub-agents
    prompts = {
        "accommodation": f"""คุณคือผู้เชี่ยวชาญด้านที่พัก ให้คำแนะนำที่พักที่เหมาะสมกับความต้องการของผู้ใช้
คำขอ: {specialized_queries.get(agent_type, query)}

โปรดให้คำแนะนำเกี่ยวกับ:
1. ประเภทที่พัก (โรงแรม, โฮสเทล, รีสอร์ท, เกสต์เฮาส์) ที่ {travel_info['destination']}
2. ช่วงราคาโดยประมาณต่อคืน (บาท)
3. ย่านหรือพื้นที่ที่เหมาะสม ใกล้สถานที่ท่องเที่ยว
4. สิ่งอำนวยความสะดวกที่ตรงกับความต้องการของผู้ใช้
5. ข้อพิจารณาพิเศษตามบริบทการเดินทาง

แนะนำที่พักอย่างน้อย 3-5 แห่ง พร้อมราคาและจุดเด่น โดยเลือกให้เหมาะกับงบประมาณ 
ให้คำแนะนำที่กระชับแต่มีข้อมูลครบถ้วน โดยมุ่งเน้นตัวเลือกที่เหมาะกับความต้องการและความชอบของผู้ใช้มากที่สุด""",
        
        "activity": f"""คุณคือผู้เชี่ยวชาญด้านกิจกรรมและสถานที่ท่องเที่ยว ให้คำแนะนำเกี่ยวกับกิจกรรมที่น่าสนใจตามความต้องการของผู้ใช้
คำขอ: {specialized_queries.get(agent_type, query)}

โปรดให้คำแนะนำเกี่ยวกับกิจกรรมและสถานที่ท่องเที่ยวที่ {travel_info['destination']} โดยครอบคลุม:
1. สถานที่ท่องเที่ยวยอดนิยมที่ไม่ควรพลาด 5-10 แห่ง
2. กิจกรรมทางวัฒนธรรม (พิพิธภัณฑ์, วัด, สถานที่ประวัติศาสตร์)
3. กิจกรรมกลางแจ้งและธรรมชาติ
4. ประสบการณ์ท้องถิ่นที่ไม่ใช่ที่ท่องเที่ยวกระแสหลัก
5. ค่าเข้าชมหรือค่าธรรมเนียมโดยประมาณ (บาท)
6. เวลาที่ใช้สำหรับแต่ละกิจกรรม

จัดเรียงกิจกรรมตามความสำคัญ และแนะนำแผนการท่องเที่ยวที่เหมาะสมสำหรับระยะเวลา {travel_info['start_date']} ถึง {travel_info['end_date']}
ให้คำแนะนำที่กระชับแต่มีข้อมูลครบถ้วน โดยมุ่งเน้นตัวเลือกที่น่าสนใจและเหมาะกับงบประมาณ {travel_info['budget']} บาท{activity_info}""",
        
        "restaurant": f"""คุณคือผู้เชี่ยวชาญด้านอาหารและร้านอาหาร ให้คำแนะนำร้านอาหารตามความต้องการของผู้ใช้
คำขอ: {specialized_queries.get(agent_type, query)}

โปรดให้คำแนะนำเกี่ยวกับร้านอาหารที่ {travel_info['destination']} โดยครอบคลุม:
1. อาหารท้องถิ่นที่ห้ามพลาดและร้านที่ขึ้นชื่อ
2. ร้านอาหารยอดนิยมสำหรับมื้อต่างๆ (อาหารเช้า, กลางวัน, เย็น)
3. ร้านอาหารในหลายระดับราคา (ประหยัด ปานกลาง หรูหรา)
4. ตลาดอาหารหรือตัวเลือกอาหารริมทาง
5. เมนูแนะนำและราคาโดยประมาณต่อมื้อ (บาท)

แนะนำร้านอาหารอย่างน้อย 8-10 ร้าน ที่มีความหลากหลายทั้งประเภทอาหารและราคา เน้นร้านที่มีชื่อเสียงและอาหารท้องถิ่น
ให้คำแนะนำที่กระชับแต่มีข้อมูลครบถ้วน ระบุทำเลที่ตั้งของร้านโดยคร่าวๆ เพื่อให้ผู้ใช้เดินทางได้สะดวก""",
        
        "transportation": f"""คุณคือผู้เชี่ยวชาญด้านการเดินทาง ให้คำแนะนำเกี่ยวกับการเดินทางตามความต้องการของผู้ใช้
คำขอ: {specialized_queries.get(agent_type, query)}

โปรดให้คำแนะนำเกี่ยวกับ:
1. วิธีเดินทางระหว่าง {travel_info['origin']} และ {travel_info['destination']} โดยละเอียด
   • ตัวเลือกการเดินทาง (เครื่องบิน, รถไฟ, รถโดยสาร, เรือ)
   • สายการบินหรือบริษัทขนส่งที่ให้บริการ
   • เวลาเดินทางโดยประมาณ
   • ราคาค่าโดยสารโดยประมาณสำหรับแต่ละตัวเลือก (บาท)
   • ความถี่ของเที่ยวบินหรือเที่ยวรถ

2. การเดินทางในพื้นที่ {travel_info['destination']}
   • ระบบขนส่งสาธารณะ
   • แท็กซี่และบริการเรียกรถ
   • บริการเช่ายานพาหนะ (รถยนต์, จักรยานยนต์)
   • ค่าใช้จ่ายโดยประมาณของแต่ละวิธี

3. คำแนะนำพิเศษ
   • เส้นทางที่ดีที่สุดสำหรับการเดินทาง
   • การจองตั๋วล่วงหน้า
   • เคล็ดลับประหยัดค่าเดินทาง

ให้คำแนะนำที่กระชับแต่มีข้อมูลครบถ้วน เน้นตัวเลือกที่สะดวก ปลอดภัย และเหมาะกับงบประมาณ {travel_info['budget']} บาท""",
        
        "travel_planner": f"""คุณคือผู้วางแผนการเดินทางผู้เชี่ยวชาญ สร้างแผนการเดินทางแบบครบวงจร
คำขอ: {query}

หลังจากวิเคราะห์คำขอของผู้ใช้ โปรดสร้างแผนการเดินทางจาก {travel_info['origin']} ไป {travel_info['destination']} 
ในวันที่ {travel_info['start_date']} ถึง {travel_info['end_date']} โดยมีงบประมาณ {travel_info['budget']} บาท

แผนการเดินทางต้องครอบคลุม:
1. การเดินทางไป-กลับ ระหว่าง {travel_info['origin']} และ {travel_info['destination']} 
   (เลือกวิธีที่ดีที่สุดทั้งด้านราคาและความสะดวก)
2. ที่พักตลอดการเดินทาง (เลือกที่พักที่เหมาะสมกับงบประมาณ แต่มีคุณภาพดี)
3. สถานที่ท่องเที่ยวและกิจกรรมในแต่ละวัน จัดเรียงตามความสำคัญและตำแหน่งที่ตั้ง
4. ร้านอาหารแนะนำสำหรับแต่ละวัน
5. การเดินทางในพื้นที่ระหว่างสถานที่ท่องเที่ยว
6. แผนสำรองในกรณีที่มีปัญหา (สภาพอากาศไม่ดี, สถานที่ปิด)
7. ค่าใช้จ่ายโดยละเอียดในแต่ละวัน แยกตามหมวดหมู่ (ที่พัก, อาหาร, เดินทาง, กิจกรรม)
8. คำแนะนำและข้อควรระวังเพื่อความปลอดภัยและประทับใจ

จัดทำตารางเวลาแบบวันต่อวันที่ชัดเจน คำนวณค่าใช้จ่ายรวมให้ไม่เกินงบประมาณ {travel_info['budget']} บาท
กรุณาจัดรูปแบบด้วยหัวข้อ "===== แผนการเดินทางของคุณ =====" และใช้การจัดรูปแบบที่อ่านง่าย
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
    logger.info(f"Sub-agent prompt: {prompt[:1000]}...")
    
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
        
        logger.info(f"Sub-agent {agent_type} response: {response.text[:100]}...")
        return response.text
    except Exception as e:
        logger.error(f"Error calling sub-agent {agent_type}: {e}")
        return f"Error: {str(e)}"
