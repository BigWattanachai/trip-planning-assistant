"""
Travel Agent: A main agent that orchestrates specialized agents.
"""
from google.adk.agents import Agent
import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

FOOD_KEYWORDS = [
    # Thai food-related words
    "อาหาร", "ร้านอาหาร", "กิน", "อร่อย", "ร้าน", "อาหารเช้า",
    "อาหารกลางวัน", "อาหารเย็น", "มื้อ", "เมนู", "จาน", "ทาน",
    "รสชาติ", "ราคา", "ค่าอาหาร", "คาเฟ่", "กาแฟ", "ขนม", "ของหวาน",
    "อาหารพื้นเมือง", "อาหารเหนือ", "อาหารใต้", "อาหารอีสาน", "อาหารทะเล",
    "สั่งอาหาร", "เชฟ", "บุฟเฟ่ต์", "ร้านอร่อย", "ของกิน", "กับข้าว", "ของทานเล่น",

    # English food-related words
    "restaurant", "food", "eat", "cafe", "breakfast", "lunch", "dinner",
    "meal", "dish", "menu", "cuisine", "delicious", "tasty", "dining", "snack",
    "dessert", "coffee shop", "street food", "local food", "chef", "buffet",
    "restaurant recommendation", "where to eat"
]

# Dictionary of Thai keywords related to activities and attractions
ACTIVITY_KEYWORDS = [
    # Thai activity-related words
    "เที่ยว", "สถานที่", "ไป", "ดู", "เดินทาง", "กิจกรรม", "น้ำตก",
    "ทะเล", "ภูเขา", "วัด", "พิพิธภัณฑ์", "ตลาด", "ช้อปปิ้ง",
    "ท่องเที่ยว", "ชายหาด", "อุทยาน", "ธรรมชาติ", "แลนด์มาร์ค", "ที่เที่ยว",
    "จุดชมวิว", "จุดถ่ายรูป", "สวนสาธารณะ", "สวนสนุก", "ปีนเขา", "เดินป่า",
    "เดินเล่น", "ชมวิว", "ศิลปะ", "วัฒนธรรม", "ประเพณี", "พระธาตุ", "เจดีย์",
    "โบราณสถาน", "ประวัติศาสตร์", "อนุสาวรีย์", "พิพิธภัณฑ์", "หมู่บ้าน", "ชุมชน",

    # English activity-related words
    "activity", "attractions", "see", "visit", "place", "temple", "market", "beach",
    "sightseeing", "tourism", "tourist spots", "landmarks", "things to do", "places to see",
    "viewpoint", "photo spot", "park", "hiking", "trekking", "adventure", "nature",
    "cultural", "historical", "heritage", "museum", "shopping", "excursion", "tour",
    "exploration", "entertainment", "sight", "destination", "attractions", "scenic",
    "what to see", "where to visit"
]

def classify_intent(user_input: str, session_id: str = None) -> str:
    """
    Classify user intent as food, activity, or general travel based on keywords and conversation context.

    TODO: Replace this simple keyword-based approach with a proper NLP intent classification model
    in production for more accurate results. Consider using a transformer-based model or a
    dedicated NLU service.

    Args:
        user_input: The user's input message
        session_id: Optional session ID to consider conversation history

    Returns:
        String indicating the intent: "restaurant", "activity", or "travel"
    """
    # Import state manager here to avoid circular imports
    try:
        # First try direct import
        from state_manager import state_manager
    except ImportError:
        try:
            # Try with backend prefix
            from backend.state_manager import state_manager
        except ImportError:
            # If all else fails, create a minimal state manager for this function
            class MinimalStateManager:
                def get_conversation_history(self, session_id, max_messages=10):
                    return []
            state_manager = MinimalStateManager()

    # Get previous messages for context if session_id provided
    previous_messages = []
    previous_agent_type = None

    if session_id:
        history = state_manager.get_conversation_history(session_id, max_messages=5)
        # Check the last few messages for context
        for i in range(len(history) - 1, -1, -1):
            message = history[i]
            previous_messages.append(message.get("content", ""))

            # Check if the last assistant message was from a specific agent
            if message.get("role") == "assistant" and "agent_type" in message:
                previous_agent_type = message.get("agent_type")
                break

    # Lower case the input for case-insensitive matching
    user_input_lower = user_input.lower()

    # Count keyword matches with weighting for phrase matches (more specific intent)
    food_score = 0
    activity_score = 0

    # Special high-priority cases first

    # Strong food-specific patterns
    if "ร้าน" in user_input_lower and "อร่อย" in user_input_lower:
        food_score += 10  # Very strong indicator for food

    if "where" in user_input_lower and "eat" in user_input_lower:
        food_score += 10  # Very strong indicator for food

    if "restaurant" in user_input_lower:
        food_score += 10  # Direct mention

    # Strong activity-specific patterns
    if "where" in user_input_lower and "visit" in user_input_lower:
        activity_score += 10  # Very strong indicator for activities

    if "attraction" in user_input_lower:
        activity_score += 10  # Direct mention

    if "ที่เที่ยว" in user_input_lower:
        activity_score += 10  # Direct mention

    # Check for food-related keywords
    for word in FOOD_KEYWORDS:
        word_lower = word.lower()
        if word_lower in user_input_lower:
            # Give higher weight to more specific phrases
            if len(word) > 5:  # Longer words/phrases get higher weight
                food_score += 2
            else:
                food_score += 1

    # Check for activity-related keywords
    for word in ACTIVITY_KEYWORDS:
        word_lower = word.lower()
        if word_lower in user_input_lower:
            # Give higher weight to more specific phrases
            if len(word) > 5:  # Longer words/phrases get higher weight
                activity_score += 2
            else:
                activity_score += 1

    # Specific phrase boost for very clear intent signals
    food_specific_phrases = [
        "ร้านอาหาร", "ที่กิน", "จะกินที่ไหน", "อาหารอร่อย",
        "where to eat", "restaurant recommend", "should i eat", "good food",
        "food in", "restaurants in", "dining", "where can i eat"
    ]

    activity_specific_phrases = [
        "ที่เที่ยว", "สถานที่ท่องเที่ยว", "อยากไปเที่ยว",
        "places to visit", "attractions", "things to do", "where to go",
        "places to see", "visit in", "tourist spots", "temples in"
    ]

    # Special case for temple (วัด) - it's a common attraction in Thailand
    if "วัด" in user_input_lower or "temple" in user_input_lower:
        activity_score += 3

    for phrase in food_specific_phrases:
        if phrase.lower() in user_input_lower:
            food_score += 5  # Strong boost for very clear food intent

    for phrase in activity_specific_phrases:
        if phrase.lower() in user_input_lower:
            activity_score += 5  # Strong boost for very clear activity intent

    # Check if the message is a follow-up question to a previous agent response
    is_follow_up = False
    follow_up_indicators = [
        "เพิ่มเติม", "แล้ว", "ด้วย", "อีก", "ต่อ", "พวกนี้",  # Thai follow-up indicators
        "more", "also", "another", "additional", "and", "what about", "those"  # English follow-up indicators
    ]

    # Simple questions are often follow-ups
    if len(user_input.split()) <= 5:
        is_follow_up = True

    # Check for follow-up phrases
    for indicator in follow_up_indicators:
        if indicator in user_input.lower():
            is_follow_up = True
            break

    # If this is a follow-up and we have a previous agent type, use that
    if is_follow_up and previous_agent_type and previous_agent_type != "travel":
        return previous_agent_type

    # Determine intent based on weighted score with thresholds
    if food_score > activity_score and food_score >= 2:
        return "restaurant"
    elif activity_score > food_score and activity_score >= 2:
        return "activity"
    else:
        # Default to general travel agent
        return "travel"

# Import the tools
from .tools.sub_agent_tools import call_activity_agent, call_restaurant_agent, call_accommodation_agent, call_transportation_agent

# Create the root agent as an orchestrator
root_agent = Agent(
    # A unique name for the agent.
    name="travel_agent",
    # The Large Language Model (LLM) that agent will use.
    model="gemini-2.0-flash-001",
    # A short description of the agent's purpose.
    description="Main agent for travel planning that orchestrates specialized agents.",
    # Instructions to set the agent's behavior.
    instruction="""
    You are a helpful travel planning assistant. Your job is to help users plan their travels to destinations
    in Thailand. You should understand the user's intent and provide appropriate information.

    You have access to four specialized agents through tools:
    1. activity_agent: Use this tool when the user asks about activities, attractions, or things to do in a destination.
    2. restaurant_agent: Use this tool when the user asks about food, restaurants, or dining in a destination.
    3. accommodation_agent: Use this tool when the user asks about hotels, accommodations, or places to stay.
    4. transportation_agent: Use this tool when the user asks about transportation, getting around, or travel logistics.

    When to use the activity_agent tool:
    - When the user asks about sightseeing, attractions, or things to do
    - When the user asks about specific activities like hiking, museums, temples, etc.
    - When the user asks for recommendations on places to visit
    - Examples: "มีที่เที่ยวอะไรบ้างในกรุงเทพ?", "แนะนำสถานที่ท่องเที่ยวในเชียงใหม่", "อยากไปเที่ยวทะเลที่ภูเก็ต"

    When to use the restaurant_agent tool:
    - When the user asks about food, restaurants, or dining options
    - When the user asks for food recommendations or where to eat
    - When the user asks about specific cuisines or dishes
    - Examples: "ร้านอาหารที่ไหนอร่อยที่สุดในกรุงเทพ?", "แนะนำร้านอาหารในเชียงใหม่หน่อย", "อยากกินอาหารทะเลในภูเก็ต"

    When to use the accommodation_agent tool:
    - When the user asks about hotels, resorts, hostels, or places to stay
    - When the user asks for accommodation recommendations
    - When the user asks about specific types of accommodations or amenities
    - Examples: "มีโรงแรมที่ไหนดีในกรุงเทพ?", "แนะนำที่พักในเชียงใหม่หน่อย", "อยากหาโรงแรมติดทะเลที่ภูเก็ต"

    When to use the transportation_agent tool:
    - When the user asks about getting around, transportation options, or travel logistics
    - When the user asks about buses, trains, taxis, or other modes of transportation
    - When the user asks about travel times, routes, or costs
    - Examples: "จะไปเชียงใหม่จากกรุงเทพได้ยังไงบ้าง?", "มีรถไฟไปภูเก็ตไหม?", "ค่าแท็กซี่จากสนามบินไปตัวเมืองเท่าไหร่?"

    If the user's request is general or combines multiple aspects of travel, you can use multiple tools
    or handle the request yourself if it's very general.

    Always be friendly, informative, and conversational. Start responses with a friendly greeting in Thai.

    If the user doesn't provide enough information, ask follow-up questions to better understand their needs.
    For example, if they just mention a destination without specifying interests, ask what kinds of activities
    or food experiences they're interested in.

    When responding about costs, always use Thai Baht (THB).

    IMPORTANT: NEVER use "xxx" or similar placeholders in your responses. Always provide real, specific 
    recommendations with actual names for hotels, restaurants, attractions, etc. If you don't know the 
    exact name of a place, provide a descriptive name based on the type of establishment and location 
    (e.g., "Riverside Boutique Hotel in Chiang Mai" instead of "โรงแรม xxx").

    Remember that your goal is to provide the most helpful and accurate information to assist
    the user in planning their travel.
    """,
    # Add the tools to the agent
    tools=[call_activity_agent, call_restaurant_agent, call_accommodation_agent, call_transportation_agent]
)
