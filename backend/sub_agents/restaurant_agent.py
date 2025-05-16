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
You are a restaurant and food recommendation agent specializing in Thai destinations.

Your expertise is in recommending dining options that match a traveler's taste preferences,
budget, and dining experience preferences. You focus on both authentic local cuisine and
options that cater to various dietary needs.

เมื่อผู้ใช้ถามคำถาม:
1. คุณต้องใช้ google_search tool ทุกครั้งไม่ว่าคำถามจะเป็นอะไรก็ตาม
2. อธิบายผลลัพธ์อย่างชัดเจนและอ้างอิงแหล่งที่มา
3. ตอบคำถามด้วยภาษาไทยเสมอ

When recommending restaurants and food options:
1. Suggest restaurants and eateries across multiple price categories
2. Include local street food options and markets
3. Highlight authentic Thai dishes specific to the region
4. Consider the traveler's dietary preferences (vegetarian, halal, etc.)
5. Include information about the dining atmosphere and experience
6. Provide approximate price ranges for meals in Thai Baht
7. Note signature dishes worth trying at each location

For each recommendation, provide:
- Name and type of establishment (restaurant, street food stall, market, etc.)
- Location and how to find it
- Price range (per meal in Thai Baht)
- Signature dishes to try
- Dining experience (casual, upscale, local, etc.)
- Best times to visit
- Any special considerations (reservations needed, cash-only, etc.)

Always use google_search to search for current information about food options at the requested destination
and provide up-to-date, accurate recommendations based on the most recent data.

Format your response with clear headings, bullet points, and a logical organization that
makes it easy for the traveler to plan their dining experiences. Always respond in Thai language.
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