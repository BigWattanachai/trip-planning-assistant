"""
State Manager: Module for managing conversation state
"""

class StateManager:
    """
    StateManager is responsible for maintaining conversation state and history.
    """
    
    def __init__(self):
        """Initialize the state manager with empty conversation stores."""
        self.conversations = {}
        self.session_states = {}
    
    def add_user_message(self, session_id, message):
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
    
    def add_agent_message(self, session_id, message, agent_type="travel"):
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
    
    def get_conversation_history(self, session_id, max_messages=None):
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
    
    def store_state(self, session_id, key, value):
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
    
    def get_state(self, session_id, key, default=None):
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
    
    def clear_session(self, session_id):
        """
        Clear all data for a session.
        
        Args:
            session_id: The session identifier
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
        
        if session_id in self.session_states:
            del self.session_states[session_id]


# Create a singleton instance
state_manager = StateManager()
