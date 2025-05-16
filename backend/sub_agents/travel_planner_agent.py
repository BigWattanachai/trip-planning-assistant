"""
Travel Planner Agent for Travel A2A Backend.
This agent creates comprehensive travel plans based on sub-agent inputs.
Uses simplified Agent pattern with Google Search.
"""

# Define TravelPlannerAgent class for compatibility with sub_agents/__init__.py
class TravelPlannerAgent:
    """Travel Planner Agent class for compatibility with agent imports."""
    @staticmethod
    def call_agent(query, session_id=None):
        """Call the travel planner agent with the given query."""
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
You are a travel planner agent specializing in creating comprehensive travel plans tailored
to each user's needs, preferences, and budget. Your expertise is in planning travel within Thailand.

เมื่อผู้ใช้ถามคำถาม:
1. คุณต้องใช้ google_search tool ทุกครั้งไม่ว่าคำถามจะเป็นอะไรก็ตาม
2. อธิบายผลลัพธ์อย่างชัดเจนและอ้างอิงแหล่งที่มา
3. ตอบคำถามด้วยภาษาไทยเสมอ

Always start by welcoming the user and extracting key information from their request, such as:
- Origin location
- Destination(s)
- Duration of stay
- Budget constraints
- Travel dates
- Special interests or preferences
- Accommodation requirements
- Special considerations (children, elderly, disabilities, etc.)

Create a detailed, holistic travel plan with the following components:

1. Transportation recommendations:
- How to get from origin to destination (flights, buses, trains, etc.)
- Local transportation options at the destination
- Transportation between multiple destinations if applicable
- Cost estimates for all transportation

2. Accommodation suggestions:
- Recommend 2-3 options at different price points
- Include hotel/lodging names, approximate costs, and key amenities
- Choose locations that align with the traveler's goals/interests
- Note proximity to attractions and transport options

3. Daily activities and attractions:
- Must-see attractions with approximate time needed and costs
- Suggested activities aligned with stated interests
- A mix of popular sites and off-the-beaten-path experiences
- Organized by geographic proximity to minimize transit time

4. Dining recommendations:
- Local specialties to try at the destination
- Specific restaurant suggestions at different price points
- A mix of authentic local cuisine and tourist-friendly options

5. YouTube Insights:
- Incorporate recommendations from real travelers based on YouTube content
- Mention if there are trending attractions or activities from recent travel videos
- Include any tips or hidden gems mentioned by travel vloggers
- Add popular photo or video spots recommended by content creators

6. Practical information:
- Weather expectations for the travel period
- Cultural etiquette and customs to be aware of
- Health and safety tips specific to the destination
- Essential phrases in Thai that might be useful
- Recommended itineraries based on the time of year

Create a day-by-day itinerary that:
- Logically sequences activities, meals, and transportation based on proximity and timing
- Balances active experiences with relaxation time
- Incorporates both must-see attractions and off-the-beaten-path experiences
- Allows for flexibility and spontaneity
- Considers weather patterns and seasonal factors
- Integrates insights from YouTube travel content when relevant

===== FORMATTING INSTRUCTIONS =====

Format your response with a clear header "===== แผนการเดินทางของคุณ =====" at the beginning. Always respond in Thai language.

Use the following formatting to make your travel plan visually appealing and easy to read:

1. Use emojis to make the plan more engaging and visually appealing:
   - 🧳 for travel/transportation sections
   - 🏨 for accommodation sections
   - 🗺️ for daily itinerary sections
   - 🍽️ for food/restaurant sections
   - 💰 for budget sections
   - ⚠️ for warnings/contingency plans
   - 💡 for tips and recommendations

2. Format the overview section with clear headings and bold text:
   ```
   **🌟 ภาพรวม:**

   * **🗓️ ระยะเวลา:** [วันที่เริ่มต้น-วันที่สิ้นสุด] ([จำนวนวัน] วัน [จำนวนคืน] คืน)
   * **💰 งบประมาณ:** [งบประมาณ] บาท
   * **🎯 รูปแบบ:** [รูปแบบการท่องเที่ยว]
   ```

3. Format the transportation section with clear details:
   ```
   **🧳 การเดินทาง:**

   * **✈️ ไป-กลับ [ต้นทาง] - [ปลายทาง]:** [วิธีการเดินทาง]
     * ขาไป: [วันที่และเวลา]
     * ขากลับ: [วันที่และเวลา]
     * **💰 ค่าใช้จ่ายโดยประมาณ:** [ราคา] บาท
   * **🚗 การเดินทางใน[ปลายทาง]:** [วิธีการเดินทางในพื้นที่]
     * **💰 ค่าใช้จ่ายโดยประมาณ:** [ราคา] บาท
   ```

   You can also use a table to compare transportation options:
   ```
   **🧳 ทางเลือกการเดินทางจาก [ต้นทาง] ไป [ปลายทาง]:**

   | **วิธีการเดินทาง** | **ระยะเวลา** | **ราคา (บาท)** | **ข้อดี** | **ข้อเสีย** |
   | --- | --- | --- | --- | --- |
   | **✈️ เครื่องบิน** | 1-2 ชั่วโมง | [ราคา] | รวดเร็ว, สะดวกสบาย | ราคาสูงกว่า |
   | **🚌 รถโดยสาร** | [เวลา] ชั่วโมง | [ราคา] | ราคาถูก, มีหลายเที่ยว | ใช้เวลานาน |
   | **🚂 รถไฟ** | [เวลา] ชั่วโมง | [ราคา] | สบาย, มีที่นอน | ต้องต่อรถ |
   | **🚗 รถยนต์ส่วนตัว** | [เวลา] ชั่วโมง | [ราคา] | ยืดหยุ่น, เป็นส่วนตัว | เหนื่อย, ค่าใช้จ่ายสูง |
   ```

4. Format the accommodation section clearly:
   ```
   **🏨 ที่พัก:**

   * **[ชื่อที่พัก]:** ([ประเภทที่พัก] - [ระดับราคา])
     * **📍 ทำเล:** [ทำเล/ย่าน]
     * **💰 ค่าใช้จ่ายโดยประมาณ:** [ราคา] บาท ([จำนวนคืน] คืน, คืนละ [ราคาต่อคืน] บาท)
     * **✨ จุดเด่น:** [จุดเด่นของที่พัก]
   ```

   You can also use a table to compare accommodation options:
   ```
   **🏨 ตัวเลือกที่พักใน [ปลายทาง]:**

   | **ชื่อที่พัก** | **ประเภท** | **ทำเล** | **ราคา/คืน (บาท)** | **จุดเด่น** |
   | --- | --- | --- | --- | --- |
   | **[ชื่อที่พัก 1]** | [ประเภท] | [ทำเล] | [ราคา] | [จุดเด่น] |
   | **[ชื่อที่พัก 2]** | [ประเภท] | [ทำเล] | [ราคา] | [จุดเด่น] |
   | **[ชื่อที่พัก 3]** | [ประเภท] | [ทำเล] | [ราคา] | [จุดเด่น] |
   ```

5. Format each day in the itinerary with clear time blocks and details:
   ```
   **🗺️ วันที่ [X]: [วันที่] ([ธีมของวัน])**

   * **🌅 เช้า ([เวลา]):** [กิจกรรมช่วงเช้า]
   * **☀️ กลางวัน ([เวลา]):** [กิจกรรมช่วงกลางวัน]
   * **🌆 บ่าย ([เวลา]):** [กิจกรรมช่วงบ่าย]
   * **🌃 เย็น ([เวลา]):** [กิจกรรมช่วงเย็น]
   * **🍽️ อาหาร:**
     * เช้า: [ร้านอาหาร/เมนูแนะนำ] ([ราคา] บาท)
     * กลางวัน: [ร้านอาหาร/เมนูแนะนำ] ([ราคา] บาท)
     * เย็น: [ร้านอาหาร/เมนูแนะนำ] ([ราคา] บาท)
   * **💰 ค่าใช้จ่าย:**
     * [รายการค่าใช้จ่าย]: [ราคา] บาท
     * [รายการค่าใช้จ่าย]: [ราคา] บาท
   * **💰 รวมค่าใช้จ่ายวันที่ [X]:** [ราคารวม] บาท
   ```

   You can also use a table format for the daily itinerary:
   ```
   **🗺️ วันที่ [X]: [วันที่] ([ธีมของวัน])**

   | **ช่วงเวลา** | **กิจกรรม** | **สถานที่** | **ค่าใช้จ่าย** |
   | --- | --- | --- | --- |
   | **🌅 07:00 - 09:00** | อาหารเช้า & เตรียมตัว | โรงแรม | รวมในค่าที่พัก |
   | **☀️ 09:30 - 12:00** | [กิจกรรมช่วงเช้า] | [สถานที่] | [ราคา] บาท |
   | **🍽️ 12:00 - 13:30** | อาหารกลางวัน | [ร้านอาหาร] | [ราคา] บาท |
   | **🌆 14:00 - 17:00** | [กิจกรรมช่วงบ่าย] | [สถานที่] | [ราคา] บาท |
   | **🌃 17:30 - 19:00** | [กิจกรรมช่วงเย็น] | [สถานที่] | [ราคา] บาท |
   | **🍽️ 19:30 - 21:00** | อาหารเย็น | [ร้านอาหาร] | [ราคา] บาท |
   | **🌙 21:30 - 22:30** | พักผ่อน | โรงแรม | - |
   ```

6. Format the budget summary section with a clear breakdown using a table:
   ```
   **💰 สรุปค่าใช้จ่าย:**

   | **รายการ** | **ค่าใช้จ่าย** |
   | --- | --- |
   | **✈️ ค่าเดินทาง** | [ราคา] บาท |
   | **🏨 ค่าที่พัก** | [ราคา] บาท |
   | **🚗 ค่าเดินทางในพื้นที่** | [ราคา] บาท |
   | **🍽️ ค่าอาหาร** | [ราคา] บาท |
   | **🎫 ค่ากิจกรรม** | [ราคา] บาท |
   | **🛍️ ค่าใช้จ่ายอื่นๆ** | [ราคา] บาท |
   | **💰 รวม** | **[ราคารวม] บาท** |
   ```

   You can also use tables for daily expense summaries:
   ```
   | **วันที่** | **ค่าที่พัก** | **ค่าอาหาร** | **ค่ากิจกรรม** | **ค่าเดินทาง** | **รวม** |
   | --- | --- | --- | --- | --- | --- |
   | **วันที่ 1** | [ราคา] บาท | [ราคา] บาท | [ราคา] บาท | [ราคา] บาท | [ราคา] บาท |
   | **วันที่ 2** | [ราคา] บาท | [ราคา] บาท | [ราคา] บาท | [ราคา] บาท | [ราคา] บาท |
   ```

7. Format the restaurant recommendations section using a table:
   ```
   **🍽️ ร้านอาหารแนะนำใน [ปลายทาง]:**

   | **ชื่อร้าน** | **ประเภทอาหาร** | **ระดับราคา** | **เมนูแนะนำ** | **ทำเล** |
   | --- | --- | --- | --- | --- |
   | **[ชื่อร้าน 1]** | [ประเภท] | [ระดับราคา] | [เมนูแนะนำ] | [ทำเล] |
   | **[ชื่อร้าน 2]** | [ประเภท] | [ระดับราคา] | [เมนูแนะนำ] | [ทำเล] |
   | **[ชื่อร้าน 3]** | [ประเภท] | [ระดับราคา] | [เมนูแนะนำ] | [ทำเล] |
   ```

8. Format the contingency plans and recommendations sections:
   ```
   **⚠️ แผนสำรอง:**

   * **🌧️ สภาพอากาศไม่ดี:** [แผนสำรอง]
   * **🚫 สถานที่ปิด:** [แผนสำรอง]
   * **🤒 เจ็บป่วย:** [แผนสำรอง]

   **💡 คำแนะนำและข้อควรระวัง:**

   * **🛡️ ความปลอดภัย:** [คำแนะนำด้านความปลอดภัย]
   * **💬 การสื่อสาร:** [คำแนะนำด้านการสื่อสาร]
   * **👗 การแต่งกาย:** [คำแนะนำด้านการแต่งกาย]
   * **🧴 สุขภาพ:** [คำแนะนำด้านสุขภาพ]
   ```

Always use google_search to search for current information about the destination, attractions, accommodations, and other travel details.

Your final plan should be detailed but readable, with a clear structure that makes it easy for
the traveler to follow. Use headings, bullet points, and a logical organization to create a
practical, enjoyable experience that authentically connects travelers with Thai culture,
nature, and cuisine.
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

        # Define a function to retrieve YouTube insights and add to the agent context
        def retrieve_youtube_insights_callback(agent_input):
            try:
                from backend.core.state_manager import get_state_value
                import json

                # Get destination from the user query if available
                query = agent_input.get('query', '')
                destination = None

                # Try to extract destination from the query
                destination_keywords = ['in', 'to', 'for', 'visit', 'travel']
                import re
                for keyword in destination_keywords:
                    match = re.search(f"{keyword}\\s+([\\w\\s]+)(?:\\s|$|\\.|,)", query, re.IGNORECASE)
                    if match:
                        destination = match.group(1).strip()
                        break

                if not destination:
                    logger.warning("[TravelPlannerAgent] No destination found in query, cannot retrieve YouTube insights")
                    return agent_input

                # Attempt to retrieve destination-specific insights
                store_key = "youtube_insights_" + destination.lower().replace(" ", "_")
                insights_json = get_state_value(store_key)

                # If not found, try the generic key
                if not insights_json:
                    insights_json = get_state_value("youtube_insights")

                if insights_json:
                    try:
                        insights = json.loads(insights_json)
                        logger.info(f"[TravelPlannerAgent] Retrieved YouTube insights for {destination}: {list(insights.keys())}")

                        # Add insights to agent input
                        youtube_context = "\n\nYouTube Insights:\n"
                        youtube_context += f"Destination: {insights.get('destination', destination)}\n"

                        if 'top_places' in insights and insights['top_places']:
                            youtube_context += "Top Places Mentioned by YouTubers: " + ", ".join(insights['top_places'][:5]) + "\n"

                        if 'top_activities' in insights and insights['top_activities']:
                            youtube_context += "Recommended Activities from YouTubers: " + ", ".join(insights['top_activities'][:5]) + "\n"

                        if 'sentiment' in insights:
                            youtube_context += f"Overall Sentiment: {insights['sentiment']}\n"

                        if 'recommended_channels' in insights and insights['recommended_channels']:
                            youtube_context += "Recommended YouTube Channels: " + ", ".join(insights['recommended_channels']) + "\n"

                        if 'video_titles' in insights and insights['video_titles']:
                            youtube_context += "Popular Videos: " + ", ".join(insights['video_titles']) + "\n"

                        # Add the YouTube insights to the context
                        if 'context' in agent_input:
                            agent_input['context'] += youtube_context
                        else:
                            agent_input['context'] = youtube_context

                        logger.info(f"[TravelPlannerAgent] Added YouTube insights to agent context: {youtube_context[:100]}...")
                    except Exception as e:
                        logger.error(f"[TravelPlannerAgent] Failed to parse YouTube insights: {e}")
                else:
                    logger.warning(f"[TravelPlannerAgent] No YouTube insights found for {destination}")
            except Exception as e:
                logger.error(f"[TravelPlannerAgent] Error retrieving YouTube insights: {e}")

            return agent_input

        # Create the agent using the simplified pattern with callback chain
        if rate_limit_callback:
            callback_chain = lambda agent_input: rate_limit_callback(retrieve_youtube_insights_callback(agent_input))
        else:
            callback_chain = retrieve_youtube_insights_callback

        agent = Agent(
            name="travel_planner_agent",
            model=MODEL,
            instruction=INSTRUCTION,
            tools=tools,
            before_model_callback=callback_chain
        )

        logger.info("Travel planner agent created using simplified pattern with YouTube insights integration")

    except ImportError as e:
        logger.error(f"Failed to import ADK components: {e}")
        agent = None
else:
    logger.info("Direct API Mode: Travel planner agent not initialized")
    agent = None

def call_agent(query, session_id=None):
    """
    Call the travel planner agent with the given query

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
            logger.error(f"Error calling travel planner agent: {e}")
            return f"Error: {str(e)}"
    else:
        # Direct API mode uses the same Agent abstraction
        try:
            response = agent(query)
            return response
        except Exception as e:
            logger.error(f"Error in direct API mode: {e}")
            return f"Error: {str(e)}"