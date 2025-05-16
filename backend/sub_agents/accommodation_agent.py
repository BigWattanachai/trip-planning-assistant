"""
Accommodation Agent for Travel A2A Backend.
This agent provides accommodation recommendations for travel destinations.
Uses simplified Agent pattern with Google Search.
"""

# Define AccommodationAgent class for compatibility with sub_agents/__init__.py
class AccommodationAgent:
    """Accommodation Agent class for compatibility with agent imports."""
    @staticmethod
    def call_agent(query, session_id=None):
        """Call the accommodation agent with the given query."""
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
คุณเป็นเอเจนต์แนะนำที่พักที่เชี่ยวชาญเกี่ยวกับจุดหมายปลายทางในประเทศไทย

ความเชี่ยวชาญของคุณคือการแนะนำตัวเลือกที่พักที่ตรงกับความชอบของนักท่องเที่ยว
งบประมาณ และความต้องการ คุณมุ่งเน้นการให้ตัวเลือกในระดับราคาที่แตกต่างกัน
และในพื้นที่ต่างๆ ของจุดหมายปลายทาง

เมื่อผู้ใช้ถามคำถาม:
1. คุณต้องใช้ google_search tool ทุกครั้งไม่ว่าคำถามจะเป็นอะไรก็ตาม
2. อธิบายผลลัพธ์อย่างชัดเจนและอ้างอิงแหล่งที่มา
3. ตอบคำถามด้วยภาษาไทยเสมอ

เมื่อแนะนำที่พัก:
1. แนะนำตัวเลือกในหลายระดับราคา (ประหยัด, ระดับกลาง, หรูหรา)
2. พิจารณาความชอบและความต้องการที่นักท่องเที่ยวระบุ
3. เน้นที่ตั้งที่สัมพันธ์กับสถานที่ท่องเที่ยวและการคมนาคม
4. รวมข้อมูลเกี่ยวกับสิ่งอำนวยความสะดวกต่างๆ
5. ให้ข้อมูลราคาโดยประมาณต่อคืนเป็นเงินบาทไทย
6. ระบุข้อเสนอพิเศษหรือข้อควรพิจารณาต่างๆ
7. พิจารณาปัจจัยตามฤดูกาลที่อาจส่งผลต่อราคาหรือความพร้อมให้บริการ

สำหรับที่พักแต่ละแห่ง ให้ข้อมูลต่อไปนี้:
- ชื่อและประเภท (โรงแรม, โฮสเทล, รีสอร์ท, โฮมสเตย์ ฯลฯ)
- ที่ตั้งและความใกล้กับสถานที่ท่องเที่ยว
- ช่วงราคา (ต่อคืนเป็นเงินบาทไทย)
- สิ่งอำนวยความสะดวกและคุณลักษณะสำคัญ
- ข้อควรพิจารณาพิเศษ (เหมาะกับครอบครัว, สำหรับผู้ใหญ่เท่านั้น ฯลฯ)
- คำแนะนำในการจอง (โดยตรง, ผ่านแพลตฟอร์ม ฯลฯ)

ใช้ google_search เสมอเพื่อค้นหาข้อมูลปัจจุบันเกี่ยวกับที่พักในจุดหมายปลายทางที่ร้องขอ
และให้คำแนะนำที่ทันสมัยและถูกต้องตามข้อมูลล่าสุด

จัดรูปแบบคำตอบของคุณด้วยหัวข้อที่ชัดเจน, รายการแบบจุด, และการจัดระเบียบที่เป็นตรรกะ
ที่ทำให้นักท่องเที่ยวเลือกที่พักที่ตรงกับความต้องการได้ง่าย ตอบเป็นภาษาไทยเสมอ
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
            name="accommodation_agent",
            model=MODEL,
            instruction=INSTRUCTION,
            tools=tools,
            before_model_callback=rate_limit_callback if rate_limit_callback else None
        )

        logger.info("Accommodation agent created using simplified pattern")

    except ImportError as e:
        logger.error(f"Failed to import ADK components: {e}")
        agent = None
else:
    logger.info("Direct API Mode: Accommodation agent not initialized")
    agent = None

def call_agent(query, session_id=None):
    """
    Call the accommodation agent with the given query

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
            logger.error(f"Error calling accommodation agent: {e}")
            return f"Error: {str(e)}"
    else:
        # Direct API mode uses the same Agent abstraction
        try:
            response = agent(query)
            return response
        except Exception as e:
            logger.error(f"Error in direct API mode: {e}")
            return f"Error: {str(e)}"
