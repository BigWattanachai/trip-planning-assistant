"""
Activity Agent for Travel A2A Backend.
This agent provides activity recommendations for travel destinations.
Uses simplified Agent pattern with Google Search.
"""

# Define ActivityAgent class for compatibility with sub_agents/__init__.py
class ActivityAgent:
    """Activity Agent class for compatibility with agent imports."""
    @staticmethod
    def call_agent(query, session_id=None):
        """Call the activity agent with the given query."""
        return call_agent(query, session_id)

import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Determine mode based on environment variable
USE_VERTEX_AI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes")
MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")

# Define the agent instructions
INSTRUCTION = """
คุณเป็นเอเจนต์แนะนำกิจกรรมที่เชี่ยวชาญเกี่ยวกับจุดหมายปลายทางท่องเที่ยวในประเทศไทย

ความเชี่ยวชาญของคุณคือการแนะนำกิจกรรม สถานที่ท่องเที่ยว และประสบการณ์ที่
ตรงกับความสนใจของนักท่องเที่ยว งบประมาณ และข้อจำกัดด้านเวลา

เมื่อผู้ใช้ถามคำถาม:
1. คุณต้องใช้ google_search tool ทุกครั้งไม่ว่าคำถามจะเป็นอะไรก็ตาม
2. อธิบายผลลัพธ์อย่างชัดเจนและอ้างอิงแหล่งที่มา
3. ตอบคำถามด้วยภาษาไทยเสมอ

เมื่อแนะนำกิจกรรม:
1. เน้นการผสมผสานระหว่างสถานที่ท่องเที่ยวยอดนิยมและสถานที่ที่ซ่อนอยู่
2. พิจารณาความสนใจที่นักท่องเที่ยวระบุ งบประมาณ และเวลาที่มี
3. จัดกลุ่มกิจกรรมตามความใกล้เคียงทางภูมิศาสตร์เพื่อลดเวลาเดินทาง
4. รวมค่าใช้จ่ายโดยประมาณและเวลาที่ต้องใช้สำหรับแต่ละกิจกรรม
5. ให้เคล็ดลับที่ใช้งานได้จริง เช่น เวลาที่ดีที่สุดในการเยี่ยมชม วิธีหลีกเลี่ยงฝูงชน ฯลฯ
6. พิจารณาปัจจัยตามฤดูกาลและสภาพอากาศเมื่อให้คำแนะนำ
7. รวมทั้งสถานที่ท่องเที่ยวทางวัฒนธรรมและธรรมชาติเมื่อเกี่ยวข้อง

คำแนะนำของคุณควรครอบคลุม:
- สถานที่ท่องเที่ยวที่ต้องไปเยี่ยมชม
- ประสบการณ์ทางวัฒนธรรม
- กิจกรรมกลางแจ้ง
- ตัวเลือกที่เหมาะสำหรับครอบครัว (ถ้าเกี่ยวข้อง)
- กิจกรรมพิเศษที่เกิดขึ้นในช่วงเวลาการเดินทาง
- จุดถ่ายภาพ
- ประสบการณ์ท้องถิ่นที่เชื่อมโยงกับวัฒนธรรมไทย

สำหรับแต่ละกิจกรรม ให้ข้อมูลต่อไปนี้:
- ชื่อและคำอธิบายสั้นๆ
- สถานที่และวิธีการเดินทางไปที่นั่น
- ค่าใช้จ่ายโดยประมาณ (เป็นเงินบาทไทย)
- ระยะเวลาที่แนะนำ
- เวลาที่ดีที่สุดในการเยี่ยมชม
- เคล็ดลับพิเศษหรือคำเตือนใดๆ

ใช้ google_search เสมอเพื่อค้นหาข้อมูลปัจจุบันเกี่ยวกับกิจกรรมในจุดหมายปลายทางที่ร้องขอ
และให้คำแนะนำที่ทันสมัยและถูกต้องตามข้อมูลล่าสุด

จัดรูปแบบคำตอบของคุณด้วยหัวข้อที่ชัดเจน, รายการแบบจุด, และการจัดระเบียบที่เป็นตรรกะ
ที่ทำให้นักท่องเที่ยววางแผนกิจกรรมของพวกเขาได้ง่าย ตอบเป็นภาษาไทยเสมอ
"""

# Only create the ADK agent if we're using Vertex AI
if USE_VERTEX_AI:
    try:
        from google.adk.agents import Agent
        from google.adk.tools import google_search

        # Import callbacks if available
        try:
            from shared_libraries.callbacks import rate_limit_callback
            from tools.store_state import store_state_tool
        except ImportError:
            try:
                from shared_libraries.callbacks import rate_limit_callback
                from tools.store_state import store_state_tool
            except ImportError:
                logger.warning("Could not import callbacks or store_state tool")
                rate_limit_callback = None
                store_state_tool = None

        # Set up tools list
        tools = [google_search]
        if store_state_tool:
            tools.append(store_state_tool)

        # Create the agent using the simplified pattern
        agent = Agent(
            name="activity_agent",
            model=MODEL,
            instruction=INSTRUCTION,
            tools=tools,
            before_model_callback=rate_limit_callback if rate_limit_callback else None
        )

        logger.info("Activity agent created using simplified pattern")

    except ImportError as e:
        logger.error(f"Failed to import ADK components: {e}")
        agent = None
else:
    logger.info("Direct API Mode: Activity agent not initialized")
    agent = None

def call_agent(query, session_id=None):
    """
    Call the activity agent with the given query

    Args:
        query: The user query
        session_id: Optional session ID for conversation tracking

    Returns:
        The agent's response
    """
    if USE_VERTEX_AI and agent:
        try:
            # ADK mode
            from google.adk.sessions import Session

            # Create or get existing session
            session = Session.get(session_id) if session_id else Session()

            # Call the agent
            response = agent.stream_query(query, session_id=session.id)
            return response
        except Exception as e:
            logger.error(f"Error calling activity agent: {e}")
            return f"Error: {str(e)}"
    else:
        # Direct API mode uses the same Agent abstraction
        try:
            response = agent(query)
            return response
        except Exception as e:
            logger.error(f"Error in direct API mode: {e}")
            return f"Error: {str(e)}"
