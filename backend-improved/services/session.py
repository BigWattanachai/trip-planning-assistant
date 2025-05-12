"""
Session management for Travel Agent Backend.
Provides a consistent interface for managing conversation state across both ADK and direct API modes.
"""
import logging
from typing import Any, Dict, List, Optional, Union
from config import settings

logger = logging.getLogger(__name__)

class SessionManager:
    """
    SessionManager is responsible for maintaining conversation state and history.
    Provides a unified interface for both ADK and direct API modes.
    """
    
    def __init__(self):
        """Initialize the session manager with empty conversation stores."""
        self.conversations = {}
        self.session_states = {}
        # ADK session service if in Vertex AI mode
        self.adk_session_service = None
        
    def initialize_for_adk(self, adk_session_service):
        """
        Initialize the session manager with an ADK session service.
        Called when running in Vertex AI mode.
        
        Args:
            adk_session_service: The ADK session service
        """
        self.adk_session_service = adk_session_service
        logger.info("SessionManager initialized with ADK session service")
    
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
        logger.debug(f"Stored state in session {session_id}: {key}={value}")
    
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
    
    def get_all_state(self, session_id: str) -> Dict[str, Any]:
        """
        Get all state values for a session.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Dictionary containing all state values
        """
        if session_id not in self.session_states:
            return {}
            
        return self.session_states[session_id]
    
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

    def ensure_adk_session(self, session_id: str, app_name: str = "travel_assistant") -> None:
        """
        Ensure an ADK session exists for this session_id.
        Only used in Vertex AI mode.
        
        Args:
            session_id: The session identifier
            app_name: The application name
        """
        if not self.adk_session_service:
            return
            
        # Create the session if it doesn't exist
        user_id = f"user_{session_id}"
        try:
            # Get or create the session
            # This will typically create the session if it doesn't exist
            session = self.adk_session_service.get_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
            
            if not session:
                # If get_session returns None or raises an exception,
                # explicitly create the session
                logger.info(f"Creating ADK session for user_id={user_id}, session_id={session_id}")
                self.adk_session_service.create_session(
                    app_name=app_name,
                    user_id=user_id,
                    session_id=session_id
                )
        except Exception as e:
            logger.warning(f"Error ensuring ADK session: {e}")
            # Try to create explicitly if an error occurred during get
            try:
                self.adk_session_service.create_session(
                    app_name=app_name, 
                    user_id=user_id,
                    session_id=session_id
                )
                logger.info(f"Created ADK session after error for user_id={user_id}, session_id={session_id}")
            except Exception as create_err:
                # If we failed to create, log but continue - the ADK code has fallbacks
                logger.warning(f"Failed to create ADK session: {create_err}")

# Create a singleton instance
_session_manager = SessionManager()

def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    return _session_manager

def initialize_adk_session_service(adk_session_service):
    """Initialize the session manager with an ADK session service."""
    _session_manager.initialize_for_adk(adk_session_service)
