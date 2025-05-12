"""
Tool for storing state in the session context.
Follows Google ADK best practices for session state management.
"""
import logging
from typing import Dict, Any, Optional

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
        
        # Validate state values
        validated_state = {}
        for key, value in state.items():
            # Ensure keys are strings
            key_str = str(key)
            
            # Handle different value types
            if isinstance(value, (str, int, float, bool, list, dict)) or value is None:
                validated_state[key_str] = value
            else:
                # Convert non-serializable types to string
                validated_state[key_str] = str(value)
        
        # Update the tool context state
        tool_context.state.update(validated_state)
    else:
        # Direct API mode - log that we can't store state directly
        logger.info(f"Direct API mode - state would be stored: {state}")
        
        # Try to get session manager in direct API mode
        try:
            from services.session import get_session_manager
            session_manager = get_session_manager()
            
            # Try to get session ID from context
            session_id = getattr(tool_context, "session_id", None) if tool_context else None
            
            # If we have a session ID, store the state
            if session_id:
                logger.info(f"Storing state in session {session_id}: {state}")
                for key, value in state.items():
                    session_manager.store_state(session_id, key, value)
        except ImportError:
            logger.warning("Could not import session manager for direct API mode")
    
    return {"status": "ok"}

# Set description for ADK
store_state_tool.description = "Store state values in the session context."
