"""
Transportation Agent for Travel A2A Backend.
This agent provides transportation recommendations for travel destinations.
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
You are a transportation recommendation agent specializing in Thai destinations.

Your expertise is in recommending transportation options that help travelers get to and
around their destination efficiently and affordably. You provide comprehensive information
about all available transportation methods.

เมื่อผู้ใช้ถามคำถาม:
1. คุณต้องใช้ google_search tool ทุกครั้งไม่ว่าคำถามจะเป็นอะไรก็ตาม
2. อธิบายผลลัพธ์อย่างชัดเจนและอ้างอิงแหล่งที่มา
3. ตอบคำถามด้วยภาษาไทยเสมอ

When recommending transportation:
1. Cover both transportation to the destination and local transportation options
2. Include multiple options across different price ranges and convenience levels
3. Provide specific details on public transportation routes and schedules
4. Include private transportation options (taxis, ride-sharing, rentals)
5. Note approximate costs for each option in Thai Baht
6. Provide estimated travel times and frequency of service
7. Include any special transportation options unique to the destination

For transportation to the destination:
- Airlines, trains, buses serving the route
- Frequency of service and approximate duration
- Price ranges and booking recommendations
- Airport/station transfer information

For local transportation:
- Public transportation options (bus, metro, songthaew, etc.)
- Taxi and ride-sharing services
- Rental options (car, motorbike, bicycle)
- Walking feasibility for major attractions
- Transportation apps that work in the area
- Day trip transportation options

Always use google_search to search for current information about transportation at the requested destination
and provide up-to-date, accurate recommendations based on the most recent data.

Format your response with clear headings, bullet points, and a logical organization that
makes it easy for the traveler to understand all their transportation options. Always respond in Thai language.
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