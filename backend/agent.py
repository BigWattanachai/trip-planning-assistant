"""
Travel Agent using Google ADK with Tavily Search Integration.
This module supports both Vertex AI (ADK) and Direct API modes.
"""

import os
import logging
import sys
import pathlib
import re
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to sys.path
parent_dir = str(pathlib.Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Add current directory to sys.path
current_dir = str(pathlib.Path(__file__).parent.absolute())
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Determine mode based on environment variable
USE_VERTEX_AI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes")
MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")

# Import Tavily search functions from tools package
try:
    # First try absolute import with backend_improve prefix
    from backend_improve.tools.tavily_search import search_with_tavily, format_tavily_results_for_agent
    TAVILY_AVAILABLE = True
    logger.info("Successfully imported Tavily search functions from backend_improve.tools")
except ImportError:
    # Try direct import
    try:
        from tools.tavily_search import search_with_tavily, format_tavily_results_for_agent
        TAVILY_AVAILABLE = True
        logger.info("Successfully imported Tavily search functions from tools")
    except ImportError as e:
        logger.warning(f"Could not import Tavily search function: {e}")
        TAVILY_AVAILABLE = False

# Only import ADK components if we're using Vertex AI
if USE_VERTEX_AI:
    try:
        import warnings
        from google.adk.agents import Agent
        from google.adk.tools import ToolContext
        from google.adk.tools.langchain_tool import LangchainTool
        
        warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")
        
        logger.info(f"ADK Mode: Using model {MODEL}")
        
        # Import shared libraries and tools
        try:
            # Try absolute imports first
            from backend_improve.shared_libraries.callbacks import rate_limit_callback
            from backend_improve.tools.store_state import store_state_tool
            from backend_improve.tools.tavily_search import get_tavily_tool_instance
            logger.info("Imported components using backend_improve prefix")
        except ImportError:
            # Try direct imports
            try:
                from shared_libraries.callbacks import rate_limit_callback
                from tools.store_state import store_state_tool
                from tools.tavily_search import get_tavily_tool_instance
                logger.info("Imported components using direct imports")
            except ImportError as e:
                logger.error(f"Failed to import tools or callbacks: {e}")
                rate_limit_callback = None
                store_state_tool = None
                get_tavily_tool_instance = None
            
        # Initialize Tavily LangChain tool for ADK if available
        adk_tavily_tool = None
        if TAVILY_AVAILABLE:
            try:
                tavily_search_instance = get_tavily_tool_instance()
                if tavily_search_instance:
                    # Wrap the LangChain tool for ADK
                    adk_tavily_tool = LangchainTool(tool=tavily_search_instance)
                    logger.info("Successfully created ADK wrapper for Tavily search tool")
            except Exception as e:
                logger.error(f"Failed to create LangchainTool wrapper for Tavily: {e}")
                adk_tavily_tool = None
        
        # Import root agent prompt
        try:
            # Try absolute import first
            from backend_improve.root_agent_prompt import PROMPT as ROOT_PROMPT
            logger.info("Imported root agent prompt using backend_improve prefix")
        except ImportError:
            # Try direct import
            try:
                from root_agent_prompt import PROMPT as ROOT_PROMPT
                logger.info("Imported root agent prompt using direct import")
            except ImportError:
                logger.error("Failed to import root agent prompt, loading default")
                ROOT_PROMPT = """
                You are a virtual travel assistant. You specialize in creating thorough travel plans
                based on user preferences and needs.
                
                Use the search_with_tavily tool to find up-to-date information about destinations,
                attractions, accommodations, and transportation options.
                
                When planning travel, consider factors like budget, season, local events, and the
                user's interests to provide personalized recommendations.
                """
        
        # Set up the list of tools for the root agent
        root_agent_tools = []
        if store_state_tool:
            root_agent_tools.append(store_state_tool)
        if adk_tavily_tool:
            root_agent_tools.append(adk_tavily_tool)
        
        # Try to import and initialize sub-agents
        try:
            # Import sub-agents if available - absolute import first
            try:
                from backend_improve.sub_agents import (
                    AccommodationAgent,
                    ActivityAgent,
                    RestaurantAgent,
                    TransportationAgent,
                    TravelPlannerAgent,
                    YouTubeInsightAgent
                )
                logger.info("Imported sub-agents using backend_improve prefix")
            except ImportError:
                # Try direct import
                from sub_agents import (
                    AccommodationAgent,
                    ActivityAgent,
                    RestaurantAgent,
                    TransportationAgent,
                    TravelPlannerAgent,
                    YouTubeInsightAgent
                )
                logger.info("Imported sub-agents using direct import")
            
            # Create a list of valid sub-agents (filter out None values)
            sub_agents = []
            if 'AccommodationAgent' in locals() and AccommodationAgent is not None:
                sub_agents.append(AccommodationAgent)
                logger.info("Added AccommodationAgent to sub-agents list")
            if 'ActivityAgent' in locals() and ActivityAgent is not None:
                sub_agents.append(ActivityAgent)
                logger.info("Added ActivityAgent to sub-agents list")
            if 'RestaurantAgent' in locals() and RestaurantAgent is not None:
                sub_agents.append(RestaurantAgent)
                logger.info("Added RestaurantAgent to sub-agents list")
            if 'TransportationAgent' in locals() and TransportationAgent is not None:
                sub_agents.append(TransportationAgent)
                logger.info("Added TransportationAgent to sub-agents list")
            if 'TravelPlannerAgent' in locals() and TravelPlannerAgent is not None:
                sub_agents.append(TravelPlannerAgent)
                logger.info("Added TravelPlannerAgent to sub-agents list")
            if 'YouTubeInsightAgent' in locals() and YouTubeInsightAgent is not None:
                sub_agents.append(YouTubeInsightAgent)
                logger.info("Added YouTubeInsightAgent to sub-agents list")
            
            # Create the root agent with valid sub-agents
            if sub_agents:
                root_agent = Agent(
                    model=MODEL,
                    name="root_agent",
                    description="Travel planning agent that creates comprehensive travel plans with up-to-date information via search",
                    instruction=ROOT_PROMPT,
                    tools=root_agent_tools,
                    sub_agents=sub_agents,
                    before_model_callback=rate_limit_callback
                )
                logger.info(f"Root agent created with {len(root_agent_tools)} tools and {len(sub_agents)} sub-agents")
            else:
                # Create root agent without sub-agents
                root_agent = Agent(
                    model=MODEL,
                    name="root_agent",
                    description="Travel planning agent that creates comprehensive travel plans with up-to-date information via search",
                    instruction=ROOT_PROMPT,
                    tools=root_agent_tools,
                    before_model_callback=rate_limit_callback
                )
                logger.info(f"Root agent created with {len(root_agent_tools)} tools but no sub-agents")
            
        except ImportError as e:
            logger.warning(f"Failed to import sub-agents: {e}. Creating root agent without sub-agents.")
            # Create root agent without sub-agents
            root_agent = Agent(
                model=MODEL,
                name="root_agent",
                description="Travel planning agent that creates comprehensive travel plans with up-to-date information via search",
                instruction=ROOT_PROMPT,
                tools=root_agent_tools,
                before_model_callback=rate_limit_callback
            )
            logger.info(f"Root agent created with {len(root_agent_tools)} tools but no sub-agents")
        
    except ImportError as e:
        logger.error(f"Failed to import ADK components: {e}")
        logger.warning("Falling back to Direct API mode")
        USE_VERTEX_AI = False
        root_agent = None
else:
    logger.info("Direct API Mode: ADK components not loaded")
    root_agent = None

def extract_travel_info(query: str) -> Dict[str, Any]:
    """
    Extract travel information from the query
    
    Args:
        query: The user query
        
    Returns:
        Dictionary with extracted travel info
    """
    # Initialize default values
    travel_info = {
        "origin": "กรุงเทพ",  # Default origin
        "destination": "ภายในประเทศไทย",  # Default destination
        "start_date": "ไม่ระบุ",
        "end_date": "ไม่ระบุ",
        "budget": "ไม่ระบุ",
        "num_travelers": 1,
        "preferences": []
    }
    
    # Extract origin
    origin_match = re.search(r"ต้นทาง:\s*([^\n]+)", query)
    if origin_match:
        travel_info["origin"] = origin_match.group(1).strip()
    
    # Extract destination
    destination_match = re.search(r"ปลายทาง:\s*([^\n]+)", query)
    if destination_match:
        travel_info["destination"] = destination_match.group(1).strip()
    
    # Extract dates
    dates_match = re.search(r"ช่วงเวลาเดินทาง:.*?วันที่:\s*(\d{4}-\d{2}-\d{2})(?:\s*ถึงวันที่\s*(\d{4}-\d{2}-\d{2}))?", query)
    if dates_match:
        travel_info["start_date"] = dates_match.group(1).strip()
        if dates_match.group(2):
            travel_info["end_date"] = dates_match.group(2).strip()
        else:
            travel_info["end_date"] = travel_info["start_date"]  # Same day trip
    
    # Extract budget
    budget_match = re.search(r"งบประมาณรวม:\s*ไม่เกิน\s*(\d+,?\d*)\s*บาท", query)
    if budget_match:
        travel_info["budget"] = budget_match.group(1).strip()
    
    # Calculate duration if start_date and end_date are available
    if travel_info["start_date"] != "ไม่ระบุ" and travel_info["end_date"] != "ไม่ระบุ":
        try:
            from datetime import datetime
            start = datetime.strptime(travel_info["start_date"], "%Y-%m-%d")
            end = datetime.strptime(travel_info["end_date"], "%Y-%m-%d")
            duration = (end - start).days + 1  # +1 to include the start day
            travel_info["duration"] = str(duration)
        except Exception as e:
            logger.warning(f"Could not calculate duration: {e}")
            travel_info["duration"] = "ไม่ระบุ"
    else:
        travel_info["duration"] = "ไม่ระบุ"
    
    return travel_info

def search_destination_info(destination: str, query_type: str = "travel") -> Dict[str, Any]:
    """
    Search for information about a destination using Tavily search.
    
    Args:
        destination: The destination to search for
        query_type: Type of query (e.g., "travel", "activities", "food", "accommodation")
        
    Returns:
        Dict: Search results
    """
    if not TAVILY_AVAILABLE:
        logger.warning(f"Tavily search not available for {destination}")
        return {"success": False, "error": "Tavily search not available"}
    
    try:
        # Build a search query based on the query type
        search_queries = {
            "travel": f"travel guide tourist information {destination} 2025",
            "activities": f"top attractions and activities in {destination} 2025",
            "food": f"best restaurants and local cuisine in {destination}",
            "accommodation": f"best places to stay hotels in {destination}",
            "transportation": f"how to get around transportation in {destination}"
        }
        
        # Use the specific query or fall back to travel
        query = search_queries.get(query_type, search_queries["travel"])
        
        # Perform the search
        logger.info(f"Searching for {query_type} information about {destination}")
        result = search_with_tavily(query, location=destination)
        
        return result
    except Exception as e:
        logger.error(f"Error searching for {destination}: {e}")
        return {"success": False, "error": str(e)}

def call_sub_agent(agent_type: str, query: str, session_id: Optional[str] = None) -> str:
    """
    Simulates calling a sub-agent in direct API mode with specialized prompts
    
    Args:
        agent_type: The type of sub-agent to call ("accommodation", "activity", "restaurant", "transportation", "travel_planner")
        query: The user query to process
        session_id: Optional session ID
        
    Returns:
        The sub-agent's response
    """
    import google.generativeai as genai
    
    # Get the API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not set. Cannot call sub-agent.")
        return "Error: GOOGLE_API_KEY not set."
    
    # Configure the Gemini API
    genai.configure(api_key=api_key)
    
    # Get the model to use
    model_name = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")
    model = genai.GenerativeModel(model_name)
    
    # Extract travel information from the query
    travel_info = extract_travel_info(query)
    logger.info(f"Extracted travel info: {travel_info}")
    
    # Ensure all required keys have default values to prevent KeyError
    default_values = {
        "origin": "กรุงเทพ",
        "destination": "ภายในประเทศไทย",
        "start_date": "ไม่ระบุ",
        "end_date": "ไม่ระบุ",
        "budget": "ไม่ระบุ",
        "duration": "ไม่ระบุ",
        "num_travelers": 1,
        "preferences": []
    }
    
    # Fill in any missing keys with default values
    for key, default_value in default_values.items():
        if key not in travel_info or travel_info[key] is None:
            travel_info[key] = default_value
            logger.info(f"Using default value for {key}: {default_value}")
    
    # Search for destination information using Tavily if available
    additional_info = ""
    if TAVILY_AVAILABLE and travel_info["destination"] != "ไม่ระบุ" and travel_info["destination"] != "ภายในประเทศไทย":
        try:
            destination = travel_info['destination']
            
            # Determine search type based on agent_type
            search_type_map = {
                "accommodation": "accommodation",
                "activity": "activities",
                "restaurant": "food",
                "transportation": "transportation",
                "travel_planner": "travel",
                "youtube_insight": "travel videos"
            }
            search_type = search_type_map.get(agent_type, "travel")
            
            # Perform search with the appropriate type
            search_results = search_destination_info(destination, search_type)
            
            if search_results and search_results.get("success", False):
                formatted_results = format_tavily_results_for_agent(search_results)
                additional_info = f"\n\nข้อมูลจากการค้นหาล่าสุด:\n{formatted_results}"
                logger.info(f"Added search results for {agent_type} agent")
            else:
                logger.warning(f"No search results for {destination}")
        except Exception as e:
            logger.error(f"Error using Tavily search: {e}")
    
    # Create specialized queries for different sub-agents
    specialized_queries = {
        "accommodation": f"""
            ฉันกำลังวางแผนเดินทางจาก {travel_info['origin']} ไป {travel_info['destination']} 
            ในวันที่ {travel_info['start_date']} ถึง {travel_info['end_date']}
            มีงบประมาณทั้งหมด {travel_info['budget']} บาท
            
            ช่วยแนะนำที่พักที่เหมาะสมได้ไหม? ต้องการที่พักคุณภาพดี ราคาคุ้มค่า ทำเลสะดวก
            พร้อมราคาต่อคืนที่เหมาะกับงบประมาณ
        """,
        
        "activity": f"""
            ฉันกำลังวางแผนเดินทางไป {travel_info['destination']} 
            ในวันที่ {travel_info['start_date']} ถึง {travel_info['end_date']}
            มีงบประมาณทั้งหมด {travel_info['budget']} บาท
            
            ช่วยแนะนำสถานที่ท่องเที่ยวสำคัญและกิจกรรมที่น่าสนใจได้ไหม?
            ต้องการเน้นสถานที่สำคัญทางวัฒนธรรม ธรรมชาติ และจุดถ่ายรูปยอดนิยม
        """,
        
        "restaurant": f"""
            ฉันกำลังวางแผนเดินทางไป {travel_info['destination']} 
            ในวันที่ {travel_info['start_date']} ถึง {travel_info['end_date']}
            มีงบประมาณทั้งหมด {travel_info['budget']} บาท
            
            ช่วยแนะนำร้านอาหารอร่อยที่ {travel_info['destination']} ได้ไหม? 
            ต้องการทราบชื่อร้าน ประเภทอาหาร เมนูเด็ดที่ต้องลอง และราคาคร่าวๆ ต่อมื้อ
            อยากได้หลากหลายราคาทั้งแบบประหยัดและร้านดังๆ
        """,
        
        "transportation": f"""
            ฉันกำลังวางแผนเดินทางจาก {travel_info['origin']} ไป {travel_info['destination']} 
            ในวันที่ {travel_info['start_date']} และกลับในวันที่ {travel_info['end_date']}
            มีงบประมาณทั้งหมด {travel_info['budget']} บาท
            
            ช่วยแนะนำวิธีการเดินทางไป-กลับระหว่าง {travel_info['origin']} และ {travel_info['destination']} ได้ไหม? 
            ต้องการทราบตัวเลือกการเดินทาง เช่น รถยนต์ เครื่องบิน รถทัวร์ พร้อมเวลาเดินทางและราคาค่าโดยสาร
            รวมทั้งวิธีเดินทางในพื้นที่ {travel_info['destination']}
        """,
        
        "travel_planner": f"""
            ช่วยสร้างแผนการเดินทางไป {travel_info['destination']} 
            เป็นเวลา {travel_info['duration']} วัน 
            งบประมาณ {travel_info['budget']} บาท
            เริ่มวันที่ {travel_info['start_date']} ถึง {travel_info['end_date']}
            
            ต้องการแผนการเดินทางแบบละเอียดแบ่งตามวัน พร้อมสถานที่ท่องเที่ยว ที่พัก ร้านอาหาร
            และการเดินทางภายในเมือง พร้อมประมาณการค่าใช้จ่ายในแต่ละวัน
        """,

        "youtube_insight": f"""
            ฉันต้องการข้อมูลเชิงลึกเกี่ยวกับการท่องเที่ยวที่ {travel_info['destination']} จากวิดีโอ YouTube
            
            ช่วยวิเคราะห์วิดีโอท่องเที่ยวเกี่ยวกับ {travel_info['destination']} และให้ข้อมูลเกี่ยวกับ:
            1. สถานที่ท่องเที่ยวยอดนิยมที่ถูกกล่าวถึงบ่อยในวิดีโอ
            2. กิจกรรมท่องเที่ยวที่ถูกแนะนำโดย YouTuber ท่องเที่ยว
            3. ข้อมูลความรู้สึกทั่วไปเกี่ยวกับจุดหมายปลายทาง (ด้านบวก/ลบ)
            4. ช่อง YouTube ยอดนิยมที่มีเนื้อหาเกี่ยวกับ {travel_info['destination']}
            5. เกร็ดน่ารู้และเคล็ดลับการท่องเที่ยวที่กล่าวถึงในวิดีโอ
            
            หากมีข้อมูลเฉพาะเกี่ยวกับการท่องเที่ยวในช่วง {travel_info['start_date']} ถึง {travel_info['end_date']} ก็จะเป็นประโยชน์มาก
        """
    }
    
    # Define prompts for different sub-agents
    prompts = {
        "accommodation": f"""คุณคือผู้เชี่ยวชาญด้านที่พัก ให้คำแนะนำที่พักที่เหมาะสมกับความต้องการของผู้ใช้
คำขอ: {specialized_queries.get(agent_type, query)}

โปรดให้คำแนะนำเกี่ยวกับ:
1. ประเภทที่พัก (โรงแรม, โฮสเทล, รีสอร์ท, เกสต์เฮาส์) ที่ {travel_info['destination']}
2. ช่วงราคาโดยประมาณต่อคืน (บาท)
3. ย่านหรือพื้นที่ที่เหมาะสม ใกล้สถานที่ท่องเที่ยว
4. สิ่งอำนวยความสะดวกที่ตรงกับความต้องการของผู้ใช้
5. ข้อพิจารณาพิเศษตามบริบทการเดินทาง

แนะนำที่พักอย่างน้อย 3-5 แห่ง พร้อมราคาและจุดเด่น โดยเลือกให้เหมาะกับงบประมาณ 
ให้คำแนะนำที่กระชับแต่มีข้อมูลครบถ้วน โดยมุ่งเน้นตัวเลือกที่เหมาะกับความต้องการและความชอบของผู้ใช้มากที่สุด{additional_info}""",
        
        "activity": f"""คุณคือผู้เชี่ยวชาญด้านกิจกรรมและสถานที่ท่องเที่ยว ให้คำแนะนำเกี่ยวกับกิจกรรมที่น่าสนใจตามความต้องการของผู้ใช้
คำขอ: {specialized_queries.get(agent_type, query)}

โปรดให้คำแนะนำเกี่ยวกับกิจกรรมและสถานที่ท่องเที่ยวที่ {travel_info['destination']} โดยครอบคลุม:
1. สถานที่ท่องเที่ยวยอดนิยมที่ไม่ควรพลาด 5-10 แห่ง
2. กิจกรรมทางวัฒนธรรม (พิพิธภัณฑ์, วัด, สถานที่ประวัติศาสตร์)
3. กิจกรรมกลางแจ้งและธรรมชาติ
4. ประสบการณ์ท้องถิ่นที่ไม่ใช่ที่ท่องเที่ยวกระแสหลัก
5. ค่าเข้าชมหรือค่าธรรมเนียมโดยประมาณ (บาท)
6. เวลาที่ใช้สำหรับแต่ละกิจกรรม

จัดเรียงกิจกรรมตามความสำคัญ และแนะนำแผนการท่องเที่ยวที่เหมาะสมสำหรับระยะเวลา {travel_info['start_date']} ถึง {travel_info['end_date']}
ให้คำแนะนำที่กระชับแต่มีข้อมูลครบถ้วน โดยมุ่งเน้นตัวเลือกที่น่าสนใจและเหมาะกับงบประมาณ {travel_info['budget']} บาท{additional_info}""",
        
        "restaurant": f"""คุณคือผู้เชี่ยวชาญด้านอาหารและร้านอาหาร ให้คำแนะนำร้านอาหารตามความต้องการของผู้ใช้
คำขอ: {specialized_queries.get(agent_type, query)}

โปรดให้คำแนะนำเกี่ยวกับร้านอาหารที่ {travel_info['destination']} โดยครอบคลุม:
1. อาหารท้องถิ่นที่ห้ามพลาดและร้านที่ขึ้นชื่อ
2. ร้านอาหารยอดนิยมสำหรับมื้อต่างๆ (อาหารเช้า, กลางวัน, เย็น)
3. ร้านอาหารในหลายระดับราคา (ประหยัด ปานกลาง หรูหรา)
4. ตลาดอาหารหรือตัวเลือกอาหารริมทาง
5. เมนูแนะนำและราคาโดยประมาณต่อมื้อ (บาท)

แนะนำร้านอาหารอย่างน้อย 8-10 ร้าน ที่มีความหลากหลายทั้งประเภทอาหารและราคา เน้นร้านที่มีชื่อเสียงและอาหารท้องถิ่น
ให้คำแนะนำที่กระชับแต่มีข้อมูลครบถ้วน ระบุทำเลที่ตั้งของร้านโดยคร่าวๆ เพื่อให้ผู้ใช้เดินทางได้สะดวก{additional_info}""",
        
        "transportation": f"""คุณคือผู้เชี่ยวชาญด้านการเดินทาง ให้คำแนะนำเกี่ยวกับการเดินทางตามความต้องการของผู้ใช้
คำขอ: {specialized_queries.get(agent_type, query)}

โปรดให้คำแนะนำเกี่ยวกับ:
1. วิธีเดินทางระหว่าง {travel_info['origin']} และ {travel_info['destination']} โดยละเอียด
   • ตัวเลือกการเดินทาง (เครื่องบิน, รถไฟ, รถโดยสาร, เรือ)
   • สายการบินหรือบริษัทขนส่งที่ให้บริการ
   • เวลาเดินทางโดยประมาณ
   • ราคาค่าโดยสารโดยประมาณสำหรับแต่ละตัวเลือก (บาท)
   • ความถี่ของเที่ยวบินหรือเที่ยวรถ

2. การเดินทางในพื้นที่ {travel_info['destination']}
   • ระบบขนส่งสาธารณะ
   • แท็กซี่และบริการเรียกรถ
   • บริการเช่ายานพาหนะ (รถยนต์, จักรยานยนต์)
   • ค่าใช้จ่ายโดยประมาณของแต่ละวิธี

3. คำแนะนำพิเศษ
   • เส้นทางที่ดีที่สุดสำหรับการเดินทาง
   • การจองตั๋วล่วงหน้า
   • เคล็ดลับประหยัดค่าเดินทาง

ให้คำแนะนำที่กระชับแต่มีข้อมูลครบถ้วน โดยมุ่งเน้นความสะดวกและความคุ้มค่าของการเดินทาง{additional_info}""",
        
        "youtube_insight": f"""คุณคือผู้เชี่ยวชาญด้านการวิเคราะห์เนื้อหาท่องเที่ยวจาก YouTube ช่วยวิเคราะห์วิดีโอและให้ข้อมูลเชิงลึกสำหรับนักท่องเที่ยว
คำขอ: {specialized_queries.get(agent_type, query)}

โปรดวิเคราะห์และให้ข้อมูลเกี่ยวกับการท่องเที่ยวที่ {travel_info['destination']} จากเนื้อหาวิดีโอ YouTube โดยครอบคลุม:

1. สถานที่ท่องเที่ยวยอดนิยม
   • สถานที่ที่ถูกกล่าวถึงบ่อยในวิดีโอต่างๆ
   • สถานที่ที่ได้รับการแนะนำจาก YouTuber ท่องเที่ยวที่มีชื่อเสียง
   • สถานที่ถ่ายรูปหรือจุดชมวิวที่สวยงาม

2. กิจกรรมท่องเที่ยวที่น่าสนใจ
   • กิจกรรมที่ได้รับการแนะนำมากที่สุดในวิดีโอ
   • ประสบการณ์ท้องถิ่นที่ไม่ควรพลาด
   • กิจกรรมที่เหมาะกับช่วงเวลาเดินทางของผู้ใช้

3. การวิเคราะห์ความรู้สึก
   • ด้านบวก: สิ่งที่นักท่องเที่ยวและ YouTuber ชื่นชมเกี่ยวกับ {travel_info['destination']}
   • ด้านลบ: ข้อควรระวังหรือปัญหาที่อาจพบในการท่องเที่ยว
   • ข้อมูลความคุ้มค่าและราคา

4. ช่อง YouTube ที่แนะนำ
   • ช่องท่องเที่ยวยอดนิยมที่มีเนื้อหาเกี่ยวกับ {travel_info['destination']}
   • วิดีโอที่น่าชมสำหรับการวางแผนท่องเที่ยว

5. เคล็ดลับพิเศษ
   • เกร็ดความรู้ที่ไม่ค่อยทราบกันทั่วไป
   • เคล็ดลับประหยัดเงินจากนักท่องเที่ยวที่มีประสบการณ์
   • คำแนะนำสำหรับการเดินทางในช่วง {travel_info['start_date']} ถึง {travel_info['end_date']}

ให้ข้อมูลที่เป็นประโยชน์และทันสมัย พร้อมระบุแหล่งที่มาจากวิดีโอ โดยเน้นข้อมูลที่จะช่วยให้การท่องเที่ยวของผู้ใช้ที่ {travel_info['destination']} สมบูรณ์และน่าจดจำมากที่สุด{additional_info}""",
        
        "travel_planner": f"""คุณคือผู้วางแผนการเดินทางผู้เชี่ยวชาญ สร้างแผนการเดินทางแบบครบวงจร
คำขอ: {query}

หลังจากวิเคราะห์คำขอของผู้ใช้ โปรดสร้างแผนการเดินทางจาก {travel_info['origin']} ไป {travel_info['destination']} 
ในวันที่ {travel_info['start_date']} ถึง {travel_info['end_date']} โดยมีงบประมาณ {travel_info['budget']} บาท

แผนการเดินทางต้องครอบคลุม:
1. การเดินทางไป-กลับ ระหว่าง {travel_info['origin']} และ {travel_info['destination']} 
   (เลือกวิธีที่ดีที่สุดทั้งด้านราคาและความสะดวก)
2. ที่พักตลอดการเดินทาง (เลือกที่พักที่เหมาะสมกับงบประมาณ แต่มีคุณภาพดี)
3. สถานที่ท่องเที่ยวและกิจกรรมในแต่ละวัน จัดเรียงตามความสำคัญและตำแหน่งที่ตั้ง
4. ร้านอาหารแนะนำสำหรับแต่ละวัน
5. การเดินทางในพื้นที่ระหว่างสถานที่ท่องเที่ยว
6. แผนสำรองในกรณีที่มีปัญหา (สภาพอากาศไม่ดี, สถานที่ปิด)
7. ค่าใช้จ่ายโดยละเอียดในแต่ละวัน แยกตามหมวดหมู่ (ที่พัก, อาหาร, เดินทาง, กิจกรรม)
8. คำแนะนำและข้อควรระวังเพื่อความปลอดภัยและประทับใจ

จัดทำตารางเวลาแบบวันต่อวันที่ชัดเจน คำนวณค่าใช้จ่ายรวมให้ไม่เกินงบประมาณ {travel_info['budget']} บาท
กรุณาจัดรูปแบบด้วยหัวข้อ "===== แผนการเดินทางของคุณ =====" และใช้การจัดรูปแบบที่อ่านง่าย{additional_info}
"""
    }
    
    # Determine which sub-agent to use based on the type
    if agent_type in prompts:
        try:
            prompt = prompts[agent_type]
        except Exception as e:
            logger.error(f"Error preparing prompt for {agent_type}: {e}")
            # Fall back to a simple prompt if formatting fails
            prompt = f"""คุณคือผู้ช่วยด้านการท่องเที่ยว โปรดให้ข้อมูลเกี่ยวกับการท่องเที่ยวที่ {travel_info.get('destination', 'ไทย')}\n\n{query}"""
    else:
        # Default to travel planner if agent type not recognized
        logger.warning(f"Unknown agent type: {agent_type}, using travel_planner")
        prompt = prompts["travel_planner"]
    
    logger.info(f"Calling sub-agent: {agent_type}")
    logger.debug(f"Sub-agent prompt: {prompt[:1000]}...")
    
    try:
        # Generate the response
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            },
        )
        
        logger.info(f"Sub-agent {agent_type} response generated")
        return response.text
    except Exception as e:
        logger.error(f"Error calling sub-agent {agent_type}: {e}")
        return f"Error: {str(e)}"
