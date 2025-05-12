"""
Callback functions for agent execution.
These can be used to control agent behavior during execution.
"""
import logging
import time
from typing import Optional, Dict, Any

# Try to import ADK-specific components
try:
    from google.adk.agents.callback_context import CallbackContext
    from google.adk.models.llm_request import LlmRequest
    from google.adk.models.llm_response import LlmResponse
    from google.genai import types
    ADK_IMPORTS = True
except ImportError:
    ADK_IMPORTS = False
    
logger = logging.getLogger(__name__)

# Rate limiting state
_last_call_time = {}

def rate_limit_callback(callback_context, llm_request) -> Optional[Any]:
    """
    Callback to implement rate limiting for model calls.
    Ensures a minimum delay between calls to avoid rate limits.
    
    Args:
        callback_context: The callback context
        llm_request: The LLM request
        
    Returns:
        None to proceed with the request, or LlmResponse to return immediately
    """
    if not ADK_IMPORTS:
        logger.warning("ADK imports not available, rate_limit_callback is a no-op")
        return None
        
    agent_name = callback_context.agent_name
    current_time = time.time()
    
    # Get the last call time for this agent
    last_time = _last_call_time.get(agent_name, 0)
    time_since_last_call = current_time - last_time
    
    # Minimum delay between calls (1 second)
    min_delay = 1.0
    
    if time_since_last_call < min_delay:
        # Wait for the remaining time
        wait_time = min_delay - time_since_last_call
        logger.info(f"Rate limiting {agent_name}: waiting for {wait_time:.2f} seconds")
        time.sleep(wait_time)
    
    # Update the last call time
    _last_call_time[agent_name] = time.time()
    
    # Allow the request to proceed
    return None

def sensitive_info_filter_callback(callback_context, llm_request) -> Optional[Any]:
    """
    Callback to filter sensitive information from requests.
    Blocks requests containing sensitive keywords.
    
    Args:
        callback_context: The callback context
        llm_request: The LLM request
        
    Returns:
        None to proceed with the request, or LlmResponse to return immediately
    """
    if not ADK_IMPORTS:
        logger.warning("ADK imports not available, sensitive_info_filter_callback is a no-op")
        return None
        
    agent_name = callback_context.agent_name
    
    # Extract the text from the latest user message in the request history
    last_user_message_text = ""
    if llm_request.contents:
        # Find the most recent message with role 'user'
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                # Assuming text is in the first part for simplicity
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break
    
    # Check for sensitive keywords
    sensitive_keywords = [
        "passport", "หนังสือเดินทาง",
        "id card", "บัตรประชาชน",
        "credit card", "บัตรเครดิต",
        "phone number", "เบอร์โทรศัพท์",
        "address", "ที่อยู่",
        "social security", "ประกันสังคม"
    ]
    
    for keyword in sensitive_keywords:
        if keyword.lower() in last_user_message_text.lower():
            logger.warning(f"Blocked request to {agent_name} containing sensitive keyword: {keyword}")
            
            # Record this in state
            callback_context.state["sensitive_info_filter_triggered"] = True
            
            # Return a response immediately
            return LlmResponse(
                content=types.Content(
                    role="model", 
                    parts=[types.Part(text="ขออภัยค่ะ ฉันไม่สามารถประมวลผลคำขอที่มีข้อมูลส่วนบุคคลได้ "
                                       "เพื่อความปลอดภัยของคุณ กรุณาหลีกเลี่ยงการแชร์ข้อมูลส่วนตัว "
                                       "เช่น หมายเลขบัตรประชาชน หนังสือเดินทาง บัตรเครดิต "
                                       "เบอร์โทรศัพท์ หรือที่อยู่ค่ะ")]
                )
            )
    
    # No sensitive information found, allow the request to proceed
    return None

def keyword_filter_callback(callback_context, llm_request, blocked_keywords=None) -> Optional[Any]:
    """
    Generic callback to filter requests containing specific keywords.
    
    Args:
        callback_context: The callback context
        llm_request: The LLM request
        blocked_keywords: List of keywords to block
        
    Returns:
        None to proceed with the request, or LlmResponse to return immediately
    """
    if not ADK_IMPORTS:
        logger.warning("ADK imports not available, keyword_filter_callback is a no-op")
        return None
    
    if not blocked_keywords:
        blocked_keywords = []
        
    agent_name = callback_context.agent_name
    
    # Extract the text from the latest user message in the request history
    last_user_message_text = ""
    if llm_request.contents:
        # Find the most recent message with role 'user'
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                # Assuming text is in the first part for simplicity
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break
    
    # Check for blocked keywords
    for keyword in blocked_keywords:
        if keyword.lower() in last_user_message_text.lower():
            logger.warning(f"Blocked request to {agent_name} containing keyword: {keyword}")
            
            # Record this in state
            callback_context.state["keyword_filter_triggered"] = True
            callback_context.state["blocked_keyword"] = keyword
            
            # Return a response immediately
            return LlmResponse(
                content=types.Content(
                    role="model", 
                    parts=[types.Part(text=f"ขออภัยค่ะ ฉันไม่สามารถตอบคำถามที่เกี่ยวข้องกับ '{keyword}' ได้")]
                )
            )
    
    # No blocked keywords found, allow the request to proceed
    return None
