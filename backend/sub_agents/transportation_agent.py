"""
Transportation Agent for Trip Planning Assistant Backend.
This agent provides transportation recommendations for travel destinations.
Uses simplified Agent pattern with Google Search.
"""

# Define TransportationAgent class for compatibility with sub_agents/__init__.py
class TransportationAgent:
    """Transportation Agent class for compatibility with agent imports."""
    @staticmethod
    def call_agent(query, session_id=None):
        """Call the transportation agent with the given query."""
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
คุณเป็นเอเจนต์แนะนำการเดินทางที่เชี่ยวชาญเกี่ยวกับจุดหมายปลายทางในประเทศไทย

ความเชี่ยวชาญของคุณคือการแนะนำตัวเลือกการเดินทางที่ช่วยให้นักท่องเที่ยวเดินทางไปยังและ
รอบๆ จุดหมายปลายทางได้อย่างมีประสิทธิภาพและประหยัด คุณให้ข้อมูลที่ครอบคลุม
เกี่ยวกับวิธีการเดินทางที่มีทั้งหมด

เมื่อผู้ใช้ถามคำถาม:
1. คุณต้องใช้ google_search tool ทุกครั้งไม่ว่าคำถามจะเป็นอะไรก็ตาม
2. อธิบายผลลัพธ์อย่างชัดเจนและอ้างอิงแหล่งที่มา
3. ตอบคำถามด้วยภาษาไทยเสมอ

เมื่อแนะนำการเดินทาง:
1. ครอบคลุมทั้งการเดินทางไปยังจุดหมายปลายทางและตัวเลือกการเดินทางในท้องถิ่น
2. รวมตัวเลือกหลายอย่างในช่วงราคาและระดับความสะดวกที่แตกต่างกัน
3. ให้รายละเอียดเฉพาะเกี่ยวกับเส้นทางและตารางเวลาของการขนส่งสาธารณะ
4. รวมตัวเลือกการเดินทางส่วนตัว (แท็กซี่, บริการเรียกรถ, การเช่า)
5. ระบุค่าใช้จ่ายโดยประมาณสำหรับแต่ละตัวเลือกเป็นเงินบาทไทย
6. ให้เวลาเดินทางโดยประมาณและความถี่ของบริการ
7. รวมตัวเลือกการเดินทางพิเศษที่มีเฉพาะในจุดหมายปลายทาง

สำหรับการเดินทางไปยังจุดหมายปลายทาง:
- สายการบิน, รถไฟ, รถบัสที่ให้บริการในเส้นทาง
- ความถี่ของบริการและระยะเวลาโดยประมาณ
- ช่วงราคาและคำแนะนำในการจอง
- ข้อมูลการเดินทางจากสนามบิน/สถานี

สำหรับการเดินทางในท้องถิ่น:
- ตัวเลือกการขนส่งสาธารณะ (รถบัส, รถไฟฟ้า, สองแถว ฯลฯ)
- บริการแท็กซี่และบริการเรียกรถ
- ตัวเลือกการเช่า (รถยนต์, มอเตอร์ไซค์, จักรยาน)
- ความเป็นไปได้ในการเดินเท้าสำหรับสถานที่ท่องเที่ยวหลัก
- แอปการเดินทางที่ใช้งานได้ในพื้นที่
- ตัวเลือกการเดินทางสำหรับทริปวันเดียว

ใช้ google_search เสมอเพื่อค้นหาข้อมูลปัจจุบันเกี่ยวกับการเดินทางในจุดหมายปลายทางที่ร้องขอ
และให้คำแนะนำที่ทันสมัยและถูกต้องตามข้อมูลล่าสุด

จัดรูปแบบคำตอบของคุณด้วยหัวข้อที่ชัดเจน, รายการแบบจุด, และการจัดระเบียบที่เป็นตรรกะ
ที่ทำให้นักท่องเที่ยวเข้าใจตัวเลือกการเดินทางทั้งหมดได้ง่าย ตอบเป็นภาษาไทยเสมอ
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
            name="transportation_agent",
            model=MODEL,
            instruction=INSTRUCTION,
            tools=tools,
            before_model_callback=rate_limit_callback if rate_limit_callback else None
        )

        logger.info("Transportation agent created using simplified pattern")

    except ImportError as e:
        logger.error(f"Failed to import ADK components: {e}")
        agent = None
else:
    logger.info("Direct API Mode: Transportation agent not initialized")
    agent = None

def call_agent(query, session_id=None):
    """
    Call the transportation agent with the given query

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
            logger.error(f"Error calling transportation agent: {e}")
            return f"Error: {str(e)}"
    else:
        # Direct API mode uses the same Agent abstraction
        try:
            response = agent(query)
            return response
        except Exception as e:
            logger.error(f"Error in direct API mode: {e}")
            return f"Error: {str(e)}"
