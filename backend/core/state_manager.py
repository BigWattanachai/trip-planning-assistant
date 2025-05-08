"""
State Manager for maintaining rich context between agent interactions.
"""
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

class StateManager:
    """
    Manages the state of a conversation across multiple agents.
    
    This class provides structured state management similar to the ADK state model,
    allowing for persistence of itinerary, user preferences, and conversation context.
    """
    
    def __init__(self):
        # Initialize with default empty state structure
        self._state = {
            "user_profile": {
                "passport_nationality": "",
                "seat_preference": "",
                "food_preference": "",
                "allergies": [],
                "likes": [],
                "dislikes": [],
                "price_sensitivity": [],
                "home": {
                    "event_type": "home",
                    "address": "",
                    "local_prefer_mode": ""
                }
            },
            "itinerary": {
                "trip_name": "",
                "start_date": "",
                "end_date": "",
                "origin": "",
                "destination": "",
                "days": []
            },
            "current_agent": "",
            "previous_agent": "",
            "conversation_history": [],
            "detected_entities": {
                "locations": set(),
                "dates": set(),
                "activities": set(),
                "foods": set()
            },
            "last_agent_responses": {}
        }
        
        # Session state dictionary for each session ID
        self._sessions = {}
    
    def get_state(self, session_id: str) -> Dict[str, Any]:
        """
        Get the state for a specific session.
        
        Args:
            session_id: The session identifier
            
        Returns:
            The state dictionary for the session
        """
        # Create a new state if this session does not exist
        if session_id not in self._sessions:
            self._sessions[session_id] = self._state.copy()
            # Deep copy for nested dictionaries
            self._sessions[session_id]["user_profile"] = self._state["user_profile"].copy()
            self._sessions[session_id]["itinerary"] = self._state["itinerary"].copy()
            self._sessions[session_id]["detected_entities"] = {k: set() for k in self._state["detected_entities"]}
        
        return self._sessions[session_id]
    
    def update_state(self, session_id: str, key: str, value: Any) -> None:
        """
        Update a specific key in the state.
        
        Args:
            session_id: The session identifier
            key: The key to update
            value: The new value
        """
        state = self.get_state(session_id)
        
        # Handle nested keys with dot notation
        if "." in key:
            parts = key.split(".")
            current = state
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            state[key] = value
    
    def add_user_message(self, session_id: str, message: str) -> None:
        """
        Add a user message to the conversation history.
        
        Args:
            session_id: The session identifier
            message: The user's message
        """
        state = self.get_state(session_id)
        state["conversation_history"].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Extract and update entities from the message
        self._extract_entities(session_id, message)
    
    def add_agent_message(self, session_id: str, message: str, agent_type: str) -> None:
        """
        Add an agent message to the conversation history.
        
        Args:
            session_id: The session identifier
            message: The agent's message
            agent_type: The type of agent that generated the message
        """
        state = self.get_state(session_id)
        
        # Update previous and current agent
        if state["current_agent"] != agent_type:
            state["previous_agent"] = state["current_agent"]
            state["current_agent"] = agent_type
        
        # Add message to conversation history
        state["conversation_history"].append({
            "role": "assistant",
            "content": message,
            "agent_type": agent_type,
            "timestamp": datetime.now().isoformat()
        })
        
        # Store the last response for each agent type
        state["last_agent_responses"][agent_type] = message
    
    def _extract_entities(self, session_id: str, message: str) -> None:
        """
        Extract entities like locations, dates, activities from a message.
        
        Args:
            session_id: The session identifier
            message: The message to extract entities from
        """
        state = self.get_state(session_id)
        message_lower = message.lower()
        
        # Very simple keyword-based extraction - this can be enhanced with NLP
        
        # Extract potential locations
        location_markers = ["ที่", "ใน", "ไป", "at", "in", "to", "visit"]
        for marker in location_markers:
            if marker in message_lower:
                # Extract the word following the marker
                index = message_lower.find(marker) + len(marker)
                if index < len(message_lower):
                    location = message_lower[index:].split()[0].strip(",.?!;:")
                    if len(location) > 2:  # Avoid very short words
                        state["detected_entities"]["locations"].add(location)
        
        # Extract potential activities
        activity_markers = ["ทำ", "เที่ยว", "activities", "visit", "do", "see", "explore"]
        for marker in activity_markers:
            if marker in message_lower:
                # Extract the word following the marker
                index = message_lower.find(marker) + len(marker)
                if index < len(message_lower):
                    activity = message_lower[index:].split()[0].strip(",.?!;:")
                    if len(activity) > 2:  # Avoid very short words
                        state["detected_entities"]["activities"].add(activity)
        
        # Extract potential foods
        food_markers = ["กิน", "อาหาร", "ร้าน", "eat", "food", "restaurant", "cuisine"]
        for marker in food_markers:
            if marker in message_lower:
                # Extract the word following the marker
                index = message_lower.find(marker) + len(marker)
                if index < len(message_lower):
                    food = message_lower[index:].split()[0].strip(",.?!;:")
                    if len(food) > 2:  # Avoid very short words
                        state["detected_entities"]["foods"].add(food)
    
    def get_context_summary(self, session_id: str) -> str:
        """
        Generate a context summary based on the session state.
        
        Args:
            session_id: The session identifier
            
        Returns:
            A string summarizing the context
        """
        state = self.get_state(session_id)
        summary_parts = []
        
        # Add itinerary summary if available
        if state["itinerary"]["origin"] and state["itinerary"]["destination"]:
            summary_parts.append(f"Trip from {state['itinerary']['origin']} to {state['itinerary']['destination']}")
            
            if state["itinerary"]["start_date"] and state["itinerary"]["end_date"]:
                summary_parts.append(f"Travel dates: {state['itinerary']['start_date']} to {state['itinerary']['end_date']}")
        
        # Add user preferences
        preferences = []
        if state["user_profile"]["food_preference"]:
            preferences.append(f"Food preference: {state['user_profile']['food_preference']}")
        if state["user_profile"]["seat_preference"]:
            preferences.append(f"Seat preference: {state['user_profile']['seat_preference']}")
        
        if preferences:
            summary_parts.append("User preferences: " + ", ".join(preferences))
        
        # Add detected entities
        for entity_type, entities in state["detected_entities"].items():
            if entities:
                # Convert set to list for easier handling
                entity_list = list(entities)
                summary_parts.append(f"{entity_type.capitalize()}: {', '.join(entity_list[:5])}" + 
                                    ("..." if len(entity_list) > 5 else ""))
        
        # Add previous agent context if available
        if state["previous_agent"]:
            summary_parts.append(f"Previous agent: {state['previous_agent']}")
        
        # Add relevant conversation context
        if len(state["conversation_history"]) > 2:
            recent_exchanges = state["conversation_history"][-4:]  # Get last 2 exchanges (4 messages)
            context = []
            for msg in recent_exchanges:
                role = "User" if msg["role"] == "user" else msg.get("agent_type", "Assistant")
                # Truncate long messages
                content = msg["content"]
                if len(content) > 100:
                    content = content[:97] + "..."
                context.append(f"{role}: {content}")
            
            summary_parts.append("Recent conversation:\n" + "\n".join(context))
        
        return "\n".join(summary_parts)
    
    def get_previous_agent_response(self, session_id: str, agent_type: str) -> Optional[str]:
        """
        Get the most recent response from a specific agent type.
        
        Args:
            session_id: The session identifier
            agent_type: The type of agent
            
        Returns:
            The most recent response from the specified agent type, or None if not found
        """
        state = self.get_state(session_id)
        return state["last_agent_responses"].get(agent_type)
    
    def get_conversation_history(self, session_id: str, max_messages: int = 10) -> List[Dict[str, Any]]:
        """
        Get the recent conversation history.
        
        Args:
            session_id: The session identifier
            max_messages: Maximum number of messages to return
            
        Returns:
            List of recent messages
        """
        state = self.get_state(session_id)
        history = state["conversation_history"]
        return history[-max_messages:] if history else []
    
    def detect_intent_from_history(self, session_id: str) -> str:
        """
        Attempt to detect the user's intent based on conversation history.
        
        Args:
            session_id: The session identifier
            
        Returns:
            String indicating the likely intent: "restaurant", "activity", or "travel"
        """
        state = self.get_state(session_id)
        
        # Check if there are detected food entities
        if state["detected_entities"]["foods"]:
            return "restaurant"
        
        # Check if there are detected activity entities
        if state["detected_entities"]["activities"]:
            return "activity"
        
        # Default to travel
        return "travel"
    
    def is_follow_up_question(self, session_id: str, message: str) -> bool:
        """
        Determine if a message is likely a follow-up to a previous question.
        
        Args:
            session_id: The session identifier
            message: The user's message
            
        Returns:
            True if the message appears to be a follow-up, False otherwise
        """
        message_lower = message.lower()
        
        # Simple question detection
        if len(message.split()) <= 5:
            return True
        
        # Check for follow-up indicators
        follow_up_indicators = [
            "เพิ่มเติม", "แล้ว", "ด้วย", "อีก", "ต่อ", "พวกนี้",  # Thai follow-up indicators
            "more", "also", "another", "additional", "and", "what about", "those"  # English follow-up indicators
        ]
        
        for indicator in follow_up_indicators:
            if indicator in message_lower:
                return True
        
        return False
    
    def get_itinerary(self, session_id: str) -> Dict[str, Any]:
        """
        Get the itinerary for a specific session.
        
        Args:
            session_id: The session identifier
            
        Returns:
            The itinerary dictionary
        """
        state = self.get_state(session_id)
        return state["itinerary"]
    
    def update_itinerary(self, session_id: str, itinerary: Dict[str, Any]) -> None:
        """
        Update the itinerary for a specific session.
        
        Args:
            session_id: The session identifier
            itinerary: The new itinerary
        """
        state = self.get_state(session_id)
        state["itinerary"] = itinerary
    
    def add_itinerary_day(self, session_id: str, day: Dict[str, Any]) -> None:
        """
        Add a day to the itinerary.
        
        Args:
            session_id: The session identifier
            day: The day to add
        """
        state = self.get_state(session_id)
        if "days" not in state["itinerary"]:
            state["itinerary"]["days"] = []
        
        state["itinerary"]["days"].append(day)
    
    def add_itinerary_event(self, session_id: str, day_number: int, event: Dict[str, Any]) -> None:
        """
        Add an event to a specific day in the itinerary.
        
        Args:
            session_id: The session identifier
            day_number: The day number
            event: The event to add
        """
        state = self.get_state(session_id)
        if "days" not in state["itinerary"]:
            state["itinerary"]["days"] = []
        
        # Find the day with the specified day_number
        day_found = False
        for day in state["itinerary"]["days"]:
            if day.get("day_number") == day_number:
                if "events" not in day:
                    day["events"] = []
                day["events"].append(event)
                day_found = True
                break
        
        # If the day was not found, create it
        if not day_found:
            state["itinerary"]["days"].append({
                "day_number": day_number,
                "date": "",  # This should be filled in properly
                "events": [event]
            })
    
    def clear_state(self, session_id: str) -> None:
        """
        Clear the state for a specific session.
        
        Args:
            session_id: The session identifier
        """
        if session_id in self._sessions:
            del self._sessions[session_id]

# Create a singleton instance
state_manager = StateManager()
