"""
Conversation History Manager for maintaining context between agent interactions.
"""
from typing import Dict, List, Optional

class ConversationHistory:
    """Manages conversation history for multi-agent systems"""
    
    def __init__(self):
        # Dictionary to store conversation history by session ID
        self._history: Dict[str, List[dict]] = {}
    
    def add_user_message(self, session_id: str, message: str) -> None:
        """
        Add a user message to the conversation history
        
        Args:
            session_id: The unique session identifier
            message: The user's message
        """
        if session_id not in self._history:
            self._history[session_id] = []
        
        self._history[session_id].append({
            "role": "user",
            "content": message
        })
        
        # Trim history if it gets too long (keep last 10 messages)
        if len(self._history[session_id]) > 20:
            self._history[session_id] = self._history[session_id][-20:]
    
    def add_agent_message(self, session_id: str, message: str, agent_type: str) -> None:
        """
        Add an agent message to the conversation history
        
        Args:
            session_id: The unique session identifier
            message: The agent's message
            agent_type: The type of agent that generated the message
        """
        if session_id not in self._history:
            self._history[session_id] = []
        
        self._history[session_id].append({
            "role": "assistant",
            "content": message,
            "agent_type": agent_type
        })
        
        # Trim history if it gets too long (keep last 10 messages)
        if len(self._history[session_id]) > 20:
            self._history[session_id] = self._history[session_id][-20:]
    
    def get_history(self, session_id: str) -> List[dict]:
        """
        Get the conversation history for a session
        
        Args:
            session_id: The unique session identifier
            
        Returns:
            List of message dictionaries in chronological order
        """
        return self._history.get(session_id, [])
    
    def get_context_summary(self, session_id: str) -> Optional[str]:
        """
        Generate a context summary for the agents based on conversation history
        
        Args:
            session_id: The unique session identifier
            
        Returns:
            A string summarizing the conversation context or None if no history exists
        """
        history = self.get_history(session_id)
        if not history:
            return None
        
        # Create a summary of the conversation
        summary_parts = []
        
        # Extract key information from the conversation
        locations = set()
        preferences = set()
        budget_mentions = []
        
        for message in history:
            content = message.get("content", "").lower()
            
            # Extract potential locations (simple approach - could be enhanced)
            location_markers = ["ที่", "ใน", "ไป", "at", "in", "to", "visit"]
            for marker in location_markers:
                if marker in content:
                    # Extract the word following the marker
                    index = content.find(marker) + len(marker)
                    if index < len(content):
                        location = content[index:].split()[0].strip(",.?!;:")
                        if len(location) > 2:  # Avoid very short words
                            locations.add(location)
            
            # Extract potential preferences
            preference_markers = ["ชอบ", "อยาก", "prefer", "like", "want", "interested"]
            for marker in preference_markers:
                if marker in content:
                    # Extract the word following the marker
                    index = content.find(marker) + len(marker)
                    if index < len(content):
                        preference = content[index:].split()[0].strip(",.?!;:")
                        if len(preference) > 2:  # Avoid very short words
                            preferences.add(preference)
            
            # Check for budget mentions
            budget_markers = ["งบ", "ราคา", "บาท", "budget", "cost", "price", "thb", "baht"]
            for marker in budget_markers:
                if marker in content:
                    # Get the sentence containing the marker
                    sentences = content.split(".")
                    for sentence in sentences:
                        if marker in sentence:
                            budget_mentions.append(sentence.strip())
        
        # Construct the summary
        if locations:
            summary_parts.append(f"Locations mentioned: {', '.join(locations)}")
        
        if preferences:
            summary_parts.append(f"Preferences mentioned: {', '.join(preferences)}")
        
        if budget_mentions:
            summary_parts.append(f"Budget information: {' '.join(budget_mentions)}")
        
        # Add general conversation history summary
        if len(history) > 0:
            last_topics = min(3, len(history))
            summary_parts.append(f"Recent conversation topics: {', '.join([msg.get('content', '')[:30] + '...' for msg in history[-last_topics:]])}")
        
        return "\n".join(summary_parts) if summary_parts else None
    
    def clear_history(self, session_id: str) -> None:
        """
        Clear the conversation history for a session
        
        Args:
            session_id: The unique session identifier
        """
        if session_id in self._history:
            del self._history[session_id]

# Create a singleton instance
conversation_history = ConversationHistory()
