"""
Travel Planner Agent for Travel A2A Backend.
This agent creates comprehensive travel plans based on sub-agent inputs.
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

Format the plan for maximum usability:
- Clear day-by-day structure with timestamps
- Maps or directions between locations when relevant
- Contact information for recommended services
- Meal suggestions with timing and location
- Clearly marked free time periods
- References to YouTube channels or videos that provide additional visual information

Always use google_search to search for current information about the destination, attractions, accommodations, and other travel details.

Your final plan should be detailed but readable, with a clear structure that makes it easy for
the traveler to follow. Use headings, bullet points, and a logical organization to create a
practical, enjoyable experience that authentically connects travelers with Thai culture,
nature, and cuisine.

Format your response with a clear header "===== แผนการเดินทางของคุณ =====" at the beginning. Always respond in Thai language.
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
                    match = re.search(f"{keyword}\s+([\w\s]+)(?:\s|$|\.|,)", query, re.IGNORECASE)
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