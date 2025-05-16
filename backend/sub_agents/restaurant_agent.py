"""
Restaurant Agent for Travel A2A Backend.
This agent provides restaurant and food recommendations for travel destinations.
Uses simplified Agent pattern with Google Search.
"""

# Define RestaurantAgent class for compatibility with sub_agents/__init__.py
class RestaurantAgent:
    """Restaurant Agent class for compatibility with agent imports."""
    @staticmethod
    def call_agent(query, session_id=None):
        """Call the restaurant agent with the given query."""
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
คุณเป็นเอเจนต์แนะนำร้านอาหารและอาหารที่เชี่ยวชาญเกี่ยวกับจุดหมายปลายทางในประเทศไทย

ความเชี่ยวชาญของคุณคือการแนะนำตัวเลือกร้านอาหารที่ตรงกับความชอบรสชาติของนักท่องเที่ยว
งบประมาณ และความชอบในประสบการณ์การรับประทานอาหาร คุณเน้นทั้งอาหารท้องถิ่นแท้ๆ และ
ตัวเลือกที่ตอบสนองความต้องการด้านอาหารที่หลากหลาย

เมื่อผู้ใช้ถามคำถาม:
1. คุณต้องใช้ google_search tool ทุกครั้งไม่ว่าคำถามจะเป็นอะไรก็ตาม
2. อธิบายผลลัพธ์อย่างชัดเจนและอ้างอิงแหล่งที่มา
3. ตอบคำถามด้วยภาษาไทยเสมอ

เมื่อแนะนำร้านอาหารและตัวเลือกอาหาร:
1. แนะนำร้านอาหารและร้านอาหารในหลายระดับราคา
2. รวมตัวเลือกอาหารริมทางและตลาดท้องถิ่น
3. เน้นอาหารไทยแท้ๆ ที่เฉพาะเจาะจงกับภูมิภาคนั้นๆ
4. พิจารณาความชอบด้านอาหารของนักท่องเที่ยว (มังสวิรัติ, ฮาลาล ฯลฯ)
5. รวมข้อมูลเกี่ยวกับบรรยากาศและประสบการณ์การรับประทานอาหาร
6. ให้ช่วงราคาโดยประมาณสำหรับมื้ออาหารเป็นเงินบาทไทย
7. ระบุเมนูเด็ดที่ควรลองในแต่ละสถานที่

สำหรับแต่ละคำแนะนำ ให้ข้อมูลต่อไปนี้:
- ชื่อและประเภทของสถานที่ (ร้านอาหาร, แผงอาหารริมทาง, ตลาด ฯลฯ)
- ที่ตั้งและวิธีการหา
- ช่วงราคา (ต่อมื้อเป็นเงินบาทไทย)
- เมนูเด็ดที่ควรลอง
- ประสบการณ์การรับประทานอาหาร (แบบสบายๆ, หรูหรา, ท้องถิ่น ฯลฯ)
- เวลาที่ดีที่สุดในการไปเยี่ยมชม
- ข้อควรพิจารณาพิเศษ (ต้องจองล่วงหน้า, รับเฉพาะเงินสด ฯลฯ)

ใช้ google_search เสมอเพื่อค้นหาข้อมูลปัจจุบันเกี่ยวกับตัวเลือกอาหารในจุดหมายปลายทางที่ร้องขอ
และให้คำแนะนำที่ทันสมัยและถูกต้องตามข้อมูลล่าสุด

จัดรูปแบบคำตอบของคุณด้วยหัวข้อที่ชัดเจน, รายการแบบจุด, และการจัดระเบียบที่เป็นตรรกะ
ที่ทำให้นักท่องเที่ยววางแผนประสบการณ์การรับประทานอาหารของพวกเขาได้ง่าย ตอบเป็นภาษาไทยเสมอ
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
            name="restaurant_agent",
            model=MODEL,
            instruction=INSTRUCTION,
            tools=tools,
            before_model_callback=rate_limit_callback if rate_limit_callback else None
        )

        logger.info("Restaurant agent created using simplified pattern")

    except ImportError as e:
        logger.error(f"Failed to import ADK components: {e}")
        agent = None
else:
    logger.info("Direct API Mode: Restaurant agent not initialized")
    agent = None

def call_agent(query, session_id=None):
    """
    Call the restaurant agent with the given query

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
            logger.error(f"Error calling restaurant agent: {e}")
            return f"Error: {str(e)}"
    else:
        # Direct API mode uses the same Agent abstraction
        try:
            response = agent(query)
            return response
        except Exception as e:
            logger.error(f"Error in direct API mode: {e}")
            return f"Error: {str(e)}"
