"""Travel Agent using Google ADK."""

import os
import logging
import sys
import pathlib
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

# Only import ADK components if we're using Vertex AI
if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes"):
    try:
        import warnings
        from google.adk.agents import Agent, AgentTool
        from google.adk.tools import ToolContext
        
        warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")
        
        MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-1.5-flash-002")
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

# Define a function to simulate sub-agent calls in direct API mode
def call_sub_agent(agent_type, query, session_id=None):
    """
    Simulates calling a sub-agent in direct API mode
    
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
    model_name = os.getenv("GOOGLE_GENAI_MODEL", "gemini-1.5-flash-002")
    model = genai.GenerativeModel(model_name)
    
    # Define prompts for different sub-agents
    prompts = {
        "accommodation": f"""คุณคือผู้เชี่ยวชาญด้านที่พัก ให้คำแนะนำที่พักที่เหมาะสมกับความต้องการของผู้ใช้
คำขอ: {query}

โปรดให้คำแนะนำเกี่ยวกับ:
1. ประเภทที่พัก (โรงแรม, โฮสเทล, รีสอร์ท, เกสต์เฮาส์)
2. ช่วงราคาโดยประมาณ
3. ย่านหรือพื้นที่ที่เหมาะสม
4. สิ่งอำนวยความสะดวกที่ตรงกับความต้องการของผู้ใช้
5. ข้อพิจารณาพิเศษตามบริบทการเดินทาง

ให้คำแนะนำที่กระชับแต่มีข้อมูลครบถ้วน โดยมุ่งเน้นตัวเลือกที่เหมาะกับความต้องการและความชอบของผู้ใช้มากที่สุด""",
        
        "activity": f"""คุณคือผู้เชี่ยวชาญด้านกิจกรรมและสถานที่ท่องเที่ยว ให้คำแนะนำเกี่ยวกับกิจกรรมที่น่าสนใจตามความต้องการของผู้ใช้
คำขอ: {query}

โปรดให้คำแนะนำเกี่ยวกับ:
1. สถานที่ท่องเที่ยวยอดนิยม
2. กิจกรรมทางวัฒนธรรม (พิพิธภัณฑ์, สถานที่ประวัติศาสตร์)
3. กิจกรรมกลางแจ้ง
4. ประสบการณ์ท้องถิ่นและจุดซ่อนเร้น
5. กิจกรรมที่เหมาะกับฤดูกาลและสภาพอากาศ
6. ค่าเข้าชมหรือค่าธรรมเนียมโดยประมาณ
7. เวลาที่ใช้สำหรับแต่ละกิจกรรม

ให้คำแนะนำที่กระชับแต่มีข้อมูลครบถ้วน โดยมุ่งเน้นตัวเลือกที่ตรงกับความสนใจและความชอบของผู้ใช้""",
        
        "restaurant": f"""คุณคือผู้เชี่ยวชาญด้านอาหารและร้านอาหาร ให้คำแนะนำร้านอาหารตามความต้องการของผู้ใช้
คำขอ: {query}

โปรดให้คำแนะนำเกี่ยวกับ:
1. อาหารท้องถิ่นและเมนูที่ต้องลอง
2. ร้านอาหารยอดนิยมสำหรับมื้อต่างๆ (อาหารเช้า, กลางวัน, เย็น)
3. ร้านอาหารในหลายระดับราคา (ประหยัด ถึง หรูหรา)
4. ประสบการณ์ทางอาหารพิเศษ (ทัวร์อาหาร, คลาสสอนทำอาหาร)
5. ตลาดอาหารหรือตัวเลือกอาหารริมทาง
6. คำแนะนำสำหรับข้อจำกัดด้านอาหารหากมีการระบุ

ให้คำแนะนำที่กระชับแต่มีข้อมูลครบถ้วน โดยมุ่งเน้นตัวเลือกที่ตรงกับรสนิยมและงบประมาณของผู้ใช้""",
        
        "transportation": f"""คุณคือผู้เชี่ยวชาญด้านการเดินทาง ให้คำแนะนำเกี่ยวกับการเดินทางตามความต้องการของผู้ใช้
คำขอ: {query}

โปรดให้คำแนะนำเกี่ยวกับ:
1. วิธีเดินทางระหว่างต้นทางและปลายทาง (เครื่องบิน, รถไฟ, รถโดยสาร)
2. ค่าใช้จ่ายโดยประมาณสำหรับแต่ละตัวเลือกการเดินทาง
3. ตัวเลือกการเดินทางในพื้นที่ (รถโดยสารสาธารณะ, แท็กซี่, บริการเรียกรถ)
4. เคล็ดลับในการนำทางระบบขนส่งท้องถิ่น
5. คำแนะนำสำหรับการเช่ายานพาหนะหากเหมาะสม
6. เวลาเดินทางโดยประมาณ

ให้คำแนะนำที่กระชับแต่มีข้อมูลครบถ้วน โดยมุ่งเน้นตัวเลือกที่ตรงกับความต้องการ งบประมาณ และความต้องการด้านประสิทธิภาพของผู้ใช้""",
        
        "travel_planner": f"""คุณคือผู้วางแผนการเดินทางผู้เชี่ยวชาญ สร้างแผนการเดินทางแบบครบวงจร
คำขอ: {query}

หลังจากวิเคราะห์คำขอของผู้ใช้ โปรดสร้างแผนการเดินทางแบบละเอียดที่รวมถึง:

1. วิธีเดินทางไปยังปลายทาง
2. คำแนะนำที่พัก
3. คำแนะนำร้านอาหาร
4. กิจกรรมและสถานที่ท่องเที่ยว
5. ตารางเวลาแบบวันต่อวันที่มีลำดับกิจกรรม อาหาร และการเดินทางอย่างมีเหตุผล
6. ค่าใช้จ่ายโดยประมาณ
7. คำแนะนำและข้อควรปฏิบัติด้านความปลอดภัย

สร้างแผนการเดินทางตามข้อมูลของผู้ใช้ โดยเน้นที่การสร้างประสบการณ์ที่สนุกและปฏิบัติได้จริง

กรุณาจัดรูปแบบด้วยหัวข้อ "===== แผนการเดินทางของคุณ ====="""
    }
    
    # Determine which sub-agent to use based on the type
    if agent_type in prompts:
        prompt = prompts[agent_type]
    else:
        # Default to travel planner if agent type not recognized
        logger.warning(f"Unknown agent type: {agent_type}, using travel_planner")
        prompt = prompts["travel_planner"]
    
    logger.info(f"Calling sub-agent: {agent_type}")
    logger.info(f"Sub-agent prompt: {prompt[:500]}...")
    
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
