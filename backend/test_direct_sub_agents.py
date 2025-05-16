"""
Test script to directly call sub-agents and log their responses.
"""

import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('direct_sub_agent_test.log')
    ]
)

logger = logging.getLogger(__name__)

# Import the call_sub_agent function
try:
    from agent import call_sub_agent
except ImportError:
    logger.error("Failed to import call_sub_agent function")
    sys.exit(1)

def test_direct_sub_agents():
    """Test sub-agents by calling them directly."""
    logger.info("Starting direct sub-agent test")
    
    # List of sub-agents to test with sample queries
    sub_agents = [
        ("accommodation", "หาที่พักราคาประหยัดในหัวหิน"),
        ("restaurant", "ร้านอาหารอร่อยในหัวหิน"),
        ("travel_planner", "วางแผนท่องเที่ยวหัวหิน 3 วัน")
    ]
    
    # Test each sub-agent
    for agent_type, query in sub_agents:
        logger.info(f"Calling {agent_type} agent with query: {query}")
        try:
            # Call the sub-agent
            response = call_sub_agent(agent_type, query)
            
            # Log the response
            logger.info(f"{agent_type.upper()} AGENT RESPONSE: {response[:100]}...")
            
            logger.info(f"Sub-agent {agent_type} call completed successfully")
        except Exception as e:
            logger.error(f"Error calling {agent_type} agent: {e}")
    
    logger.info("All direct sub-agent tests completed")

if __name__ == "__main__":
    test_direct_sub_agents()
