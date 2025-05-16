"""
Sub-agent router tool for VERTEXAI mode.
This tool allows the root agent to call sub-agents in VERTEXAI mode,
working around the limitation that Vertex AI only supports multiple tools
when they are all search tools.
"""

import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

def call_sub_agent_tool(agent_type: str, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Call a sub-agent with the given query.
    
    This tool routes requests to the appropriate sub-agent based on the agent_type.
    It works around the Vertex AI limitation that multiple tools must all be search tools.
    
    Args:
        agent_type: The type of sub-agent to call (accommodation, activity, restaurant, etc.)
        query: The query to send to the sub-agent
        session_id: Optional session ID for stateful interactions
        
    Returns:
        Dict containing the sub-agent's response
    """
    try:
        # Import the call_sub_agent function from agent.py
        from agent import call_sub_agent, log_sub_agent_activity
        
        # Log the sub-agent request
        logger.info(f"🔍 SUB-AGENT TOOL: Calling {agent_type}_agent with query: {query}")
        
        # Call the sub-agent
        response = call_sub_agent(agent_type, query, session_id)
        
        # Log the sub-agent response
        logger.info(f"✅ SUB-AGENT TOOL: Received response from {agent_type}_agent")
        
        # Return the response in a structured format
        return {
            "status": "success",
            "agent_type": agent_type,
            "response": response
        }
    except Exception as e:
        error_message = f"Error calling {agent_type}_agent: {str(e)}"
        logger.error(f"❌ SUB-AGENT TOOL: {error_message}")
        return {
            "status": "error",
            "agent_type": agent_type,
            "error": error_message
        }
