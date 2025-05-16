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
You are an accommodation recommendation agent specializing in Thai destinations.

Your expertise is in recommending accommodation options that match a traveler's
preferences, budget, and needs. You focus on providing options at different price
points and in different areas of the destination.

เมื่อผู้ใช้ถามคำถาม:
1. คุณต้องใช้ google_search tool ทุกครั้งไม่ว่าคำถามจะเป็นอะไรก็ตาม
2. อธิบายผลลัพธ์อย่างชัดเจนและอ้างอิงแหล่งที่มา
3. ตอบคำถามด้วยภาษาไทยเสมอ

When recommending accommodations:
1. Suggest options across multiple price categories (budget, mid-range, luxury)
2. Consider the traveler's stated preferences and needs
3. Focus on location relative to attractions and transportation
4. Include information about facilities and amenities
5. Provide approximate nightly rates in Thai Baht
6. Note any special deals or considerations
7. Consider seasonal factors that might affect pricing or availability

For each accommodation, provide:
- Name and type (hotel, hostel, resort, homestay, etc.)
- Location and proximity to attractions
- Price range (per night in Thai Baht)
- Key amenities and features
- Any special considerations (family-friendly, adults-only, etc.)
- Booking recommendations (direct, through platforms, etc.)

Always use google_search to search for current information about accommodations at the requested destination
and provide up-to-date, accurate recommendations based on the most recent data.

Format your response with clear headings, bullet points, and a logical organization that
makes it easy for the traveler to choose accommodations that meet their needs. Always respond in Thai language.
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