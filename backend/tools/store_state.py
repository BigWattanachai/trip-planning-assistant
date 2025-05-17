"""
Store State Tool for Trip Planning Assistant Application.
This module provides tools for storing state in agent contexts.
"""

import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

def store_state(state: Dict[str, Any], tool_context: Optional[Any] = None) -> Dict[str, str]:
    """
    Store state values in the appropriate context.
    In ADK mode, it stores in the ToolContext.
    In Direct API mode, it logs the state for debugging.
    
    Args:
        state: Dictionary of state values to store
        tool_context: The ToolContext object in ADK mode (optional)
    
    Returns:
        Dict[str, str]: Status response
    """
    logger.info(f"Storing state: {state}")
    
    # If we have a tool_context (ADK mode), update its state
    if tool_context is not None:
        tool_context.state.update(state)
        logger.info(f"State stored in ADK ToolContext: {list(state.keys())}")
    else:
        # In Direct API mode, just log the state
        logger.info(f"State would be stored (Direct API mode): {state}")
    
    return {"status": "ok"}

# Define an ADK-compatible store_state_tool with description
store_state_tool = store_state
setattr(store_state_tool, "description", "Store state values in the agent context.")
