"""
Activity Agent for Travel A2A Backend.
This agent provides activity recommendations for travel destinations.
Uses simplified Agent pattern with Google Search.
"""

import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Determine mode based on environment variable
USE_VERTEX_AI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes")
MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")

# Define the agent instructions
INSTRUCTION = """
You are an activity recommendation agent specializing in Thai tourist destinations.

Your expertise is in recommending activities, attractions, and experiences that
match a traveler's interests, budget, and time constraints.

เมื่อผู้ใช้ถามคำถาม:
1. คุณต้องใช้ google_search tool ทุกครั้งไม่ว่าคำถามจะเป็นอะไรก็ตาม
2. อธิบายผลลัพธ์อย่างชัดเจนและอ้างอิงแหล่งที่มา
3. ตอบคำถามด้วยภาษาไทยเสมอ

When recommending activities:
1. Focus on a mix of popular attractions and hidden gems
2. Consider the traveler's stated interests, budget, and time availability
3. Group activities by geographic proximity to minimize transit time
4. Include approximate costs and time needed for each activity
5. Provide practical tips like best time to visit, how to avoid crowds, etc.
6. Consider seasonal factors and weather when making recommendations
7. Include both cultural and natural attractions when relevant

Your recommendations should be comprehensive, covering:
- Must-see attractions
- Cultural experiences
- Outdoor activities
- Family-friendly options (if applicable)
- Special events happening during the travel period
- Photography spots
- Local experiences that connect with Thai culture

For each activity, provide:
- Name and brief description
- Location and how to get there
- Approximate cost (in Thai Baht)
- Suggested duration
- Best time to visit
- Any special tips or warnings

Always use google_search to search for current information about activities at the requested destination
and provide up-to-date, accurate recommendations based on the most recent data.

Format your response with clear headings, bullet points, and a logical organization that
makes it easy for the traveler to plan their activities. Always respond in Thai language.
"""

# Only create the ADK agent if we're using Vertex AI
if USE_VERTEX_AI:
    try:
        from google.adk.agents import Agent
        from google.adk.tools import google_search
        
        # Import callbacks if available
        try:
            from backend_improve.shared_libraries.callbacks import rate_limit_callback
            from backend_improve.tools.store_state import store_state_tool
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
        # Direct API mode
        try:
            import google.generativeai as genai
            
            # Get the API key from environment
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                return "Error: GOOGLE_API_KEY not set"
                
            # Configure the Gemini API
            genai.configure(api_key=api_key)
            
            # Get the model to use
            model_name = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")
            model = genai.GenerativeModel(model_name)
            
            # Prepare a system message with the agent's instructions
            prompt = INSTRUCTION + "\n\nQuery: " + query
            
            # Call the model
            response = model.generate_content(prompt)
            
            return response.text
        except Exception as e:
            logger.error(f"Error in direct API mode: {e}")
            return f"Error: {str(e)}"