"""
State Manager: Module for managing conversation state
"""

import logging
from typing import List, Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

class StateManager:
    """
    StateManager is responsible for maintaining conversation state and history.
    It stores messages and other state variables for each session.
    """
    
    def __init__(self):
        """Initialize the state manager with empty conversation stores."""
        self.conversations = {}
        self.session_states = {}
        logger.info("StateManager initialized")
    
    def add_user_message(self, session_id: str, message: str) -> None:
        """
        Add a user message to the conversation history.
        
        Args:
            session_id: The session identifier
            message: The user message content
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            "role": "user",
            "content": message
        })
        logger.debug(f"Added user message to session {session_id}: {message[:50]}...")
    
    def add_agent_message(self, session_id: str, message: str, agent_type: str = "travel") -> None:
        """
        Add an agent message to the conversation history.
        
        Args:
            session_id: The session identifier
            message: The agent message content
            agent_type: The type of agent that generated the message
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            "role": "assistant",
            "content": message,
            "agent_type": agent_type
        })
        logger.debug(f"Added {agent_type} agent message to session {session_id}: {message[:50]}...")
    
    def get_conversation_history(self, session_id: str, max_messages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the conversation history for a session.
        
        Args:
            session_id: The session identifier
            max_messages: Optional maximum number of messages to return
            
        Returns:
            A list of message objects
        """
        if session_id not in self.conversations:
            return []
        
        history = self.conversations[session_id]
        if max_messages is not None:
            return history[-max_messages:]
        return history
    
    def store_state(self, session_id: str, key: str, value: Any) -> None:
        """
        Store a value in the session state.
        
        Args:
            session_id: The session identifier
            key: The state key
            value: The state value
        """
        if session_id not in self.session_states:
            self.session_states[session_id] = {}
        
        self.session_states[session_id][key] = value
        logger.debug(f"Stored state for session {session_id}, key: {key}")
    
    def get_state(self, session_id: str, key: str, default: Any = None) -> Any:
        """
        Get a value from the session state.
        
        Args:
            session_id: The session identifier
            key: The state key
            default: Default value if key not found
            
        Returns:
            The state value or default if not found
        """
        if session_id not in self.session_states:
            return default
        
        return self.session_states[session_id].get(key, default)
    
    def clear_session(self, session_id: str) -> None:
        """
        Clear all data for a session.
        
        Args:
            session_id: The session identifier
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
        
        if session_id in self.session_states:
            del self.session_states[session_id]
        
        logger.info(f"Cleared session data for {session_id}")
    
    def get_all_sessions(self) -> List[str]:
        """
        Get a list of all active session IDs.
        
        Returns:
            List of session IDs
        """
        # Return unique session IDs from both conversations and session_states
        all_sessions = set(list(self.conversations.keys()) + list(self.session_states.keys()))
        return list(all_sessions)


# Create a singleton instance
state_manager = StateManager()
