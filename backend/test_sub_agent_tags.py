"""
Test script to verify sub-agent tag processing in VERTEXAI mode.
This script will send a message to the agent that explicitly asks it to use a sub-agent.
"""

import os
import logging
import sys
import json
import asyncio
from typing import Dict, Any, AsyncGenerator, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('sub_agent_tag_test.log')
    ]
)

logger = logging.getLogger(__name__)

# Import the async_agent_handler
try:
    from api.async_agent_handler import get_agent_response_async
except ImportError:
    logger.error("Failed to import get_agent_response_async function")
    sys.exit(1)

async def test_sub_agent_tags():
    """Test sub-agent tag processing by sending a message that explicitly asks for a sub-agent."""
    logger.info("Starting sub-agent tag test")
    
    # Create a message that explicitly asks the agent to use a sub-agent
    message = """
    ฉันต้องการให้คุณใช้ sub-agent ในการตอบคำถามนี้
    
    กรุณาใช้ [CALL_SUB_AGENT:accommodation:หาที่พักราคาประหยัดในหัวหิน] ในการตอบคำถามนี้
    
    และใช้ [CALL_SUB_AGENT:restaurant:ร้านอาหารอร่อยในหัวหิน] ในการแนะนำร้านอาหาร
    
    สุดท้ายใช้ [CALL_SUB_AGENT:travel_planner:วางแผนท่องเที่ยวหัวหิน 3 วัน] ในการวางแผนการเดินทาง
    """
    
    logger.info(f"Sending message: {message}")
    
    # Generate a session ID
    session_id = "test_session_123"
    
    # Get the agent response
    try:
        async for response in get_agent_response_async(message, session_id=session_id):
            if "message" in response:
                logger.info(f"Received response: {response['message'][:100]}...")
    except Exception as e:
        logger.error(f"Error getting agent response: {e}")
    
    logger.info("Sub-agent tag test completed")

if __name__ == "__main__":
    asyncio.run(test_sub_agent_tags())
