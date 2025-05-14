"""
Travel Planner Agent for Travel A2A Backend (Improved).
This agent creates comprehensive travel plans based on sub-agent inputs.
"""

import os
import sys
import pathlib
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to allow imports
parent_dir = str(pathlib.Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Add current directory to sys.path
current_dir = str(pathlib.Path(__file__).parent.absolute())
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import Tavily search functions if available
try:
    from backend_improve.tools.tavily_search import search_with_tavily, format_tavily_results_for_agent
    TAVILY_AVAILABLE = True
    logger.info("Successfully imported Tavily search functions in travel planner agent")
except ImportError:
    try:
        from tools.tavily_search import search_with_tavily, format_tavily_results_for_agent
        TAVILY_AVAILABLE = True
        logger.info("Successfully imported Tavily search functions with direct import")
    except ImportError as e:
        logger.warning(f"Could not import Tavily search function in travel planner agent: {e}")
        TAVILY_AVAILABLE = False

# Only import ADK components if we're using Vertex AI
if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes"):
    try:
        from google.adk.agents import Agent
        from google.adk.tools.langchain_tool import LangchainTool
        
        # Import the model
        try:
            from backend_improve import MODEL
        except (ImportError, ValueError):
            MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")
        
        # Import tools and callbacks
        try:
            from backend_improve.shared_libraries.callbacks import rate_limit_callback
            from backend_improve.tools.store_state import store_state_tool
            from backend_improve.tools.tavily_search import get_tavily_tool_instance
        except (ImportError, ValueError):
            try:
                from shared_libraries.callbacks import rate_limit_callback
                from tools.store_state import store_state_tool
                from tools.tavily_search import get_tavily_tool_instance
            except ImportError as e:
                logger.error(f"Failed to import tools or callbacks: {e}")
                rate_limit_callback = None
                store_state_tool = None
                get_tavily_tool_instance = None
        
        # Setup Tavily tool using our initialized instance
        adk_tavily_tool = None
        if TAVILY_AVAILABLE:
            try:
                tavily_search_instance = get_tavily_tool_instance()
                if tavily_search_instance:
                    adk_tavily_tool = LangchainTool(tool=tavily_search_instance)
                    logger.info("Successfully created ADK wrapper for Tavily search tool")
            except Exception as e:
                logger.error(f"Failed to create LangchainTool wrapper for Tavily: {e}")
                adk_tavily_tool = None
        
        # Import the prompt
        PROMPT = """
        You are a travel planner agent specializing in creating comprehensive travel plans tailored
        to each user's needs, preferences, and budget. Your expertise is in planning travel within Thailand.
        
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
        
        Call the store_state tool with key 'travel_plan' and the value as your comprehensive travel plan.
        
        Your final plan should be detailed but readable, with a clear structure that makes it easy for
        the traveler to follow. Use headings, bullet points, and a logical organization to create a
        practical, enjoyable experience that authentically connects travelers with Thai culture,
        nature, and cuisine.
        
        Format your response with a clear header "===== แผนการเดินทางของคุณ =====" at the beginning.
        """
        
        # Create the agent
        # Setup tools list with available tools
        tools = []
        if store_state_tool:
            tools.append(store_state_tool)
        if adk_tavily_tool is not None:
            tools.append(adk_tavily_tool)
            
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
            
        TravelPlannerAgent = Agent(
            model=MODEL,
            name="travel_planner_agent",
            description="Create comprehensive travel plans based on recommendations from specialized agents.",
            instruction=PROMPT,
            tools=tools,
            before_model_callback=lambda agent_input: rate_limit_callback(retrieve_youtube_insights_callback(agent_input)),
        )
        logger.info(f"Travel planner agent created successfully with {len(tools)} tools and YouTube insights integration")
        
    except ImportError as e:
        logger.error(f"Failed to import ADK components for travel planner agent: {e}")
        TravelPlannerAgent = None
else:
    logger.info("Direct API Mode: Travel planner agent not loaded with ADK")
    TravelPlannerAgent = None
