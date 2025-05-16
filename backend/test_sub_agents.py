"""
Test script to verify sub-agent calls in VERTEXAI mode.
This script will call each sub-agent directly and log the results.
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
        logging.FileHandler('sub_agent_test.log')
    ]
)

logger = logging.getLogger(__name__)

# Import the call_sub_agent function
try:
    from agent import call_sub_agent, log_sub_agent_activity
except ImportError:
    logger.error("Failed to import call_sub_agent function")
    sys.exit(1)

def test_all_sub_agents():
    """Test all sub-agents by calling them directly."""
    logger.info("Starting sub-agent tests")
    
    # List of sub-agents to test with sample queries
    sub_agents = [
        ("accommodation", "หาที่พักราคาประหยัดในหัวหิน"),
        ("activity", "แนะนำสถานที่ท่องเที่ยวในหัวหิน"),
        ("restaurant", "ร้านอาหารอร่อยในหัวหิน"),
        ("transportation", "วิธีเดินทางจากกรุงเทพไปหัวหิน"),
        ("travel_planner", "วางแผนท่องเที่ยวหัวหิน 3 วัน"),
        ("youtube_insight", "วิดีโอแนะนำการท่องเที่ยวหัวหิน")
    ]
    
    # Test each sub-agent
    for agent_type, query in sub_agents:
        logger.info(f"Testing {agent_type} agent with query: {query}")
        try:
            # Log the sub-agent request
            log_sub_agent_activity(agent_type, "request", query)
            
            # Call the sub-agent
            response = call_sub_agent(agent_type, query)
            
            # Log the sub-agent response
            log_sub_agent_activity(agent_type, "response", response)
            
            logger.info(f"Sub-agent {agent_type} test completed successfully")
        except Exception as e:
            logger.error(f"Error testing {agent_type} agent: {e}")
    
    logger.info("All sub-agent tests completed")

if __name__ == "__main__":
    test_all_sub_agents()
