"""
Tool for storing state in the session context.
Follows Google ADK best practices for session state management.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def store_state_tool(state: Dict[str, Any], tool_context=None) -> Dict[str, str]:
    """
    Stores new state values in the ToolContext.
    Compatible with both ADK and direct API modes.
    
    Args:
        state: Dictionary of state values to store
        tool_context: ToolContext object (provided automatically by ADK)
        
    Returns:
        Status dictionary
    """
    if tool_context:
        # ADK mode - store in tool_context.state
        logger.info(f"Storing state in ADK ToolContext: {state}")
        tool_context.state.update(state)
    else:
        # Direct API mode - log that we can't store state directly
        logger.info(f"Direct API mode - state would be stored: {state}")
    
    return {"status": "ok"}

# Set description for ADK
store_state_tool.description = "Store state values in the session context."
