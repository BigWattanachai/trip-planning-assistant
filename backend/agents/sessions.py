"""
Custom implementation of session management classes for Google ADK.
This is needed because the current version of Google ADK doesn't have the SessionManager class.
"""
from typing import Any, Dict, List, Optional
import json
import os
import uuid
from datetime import datetime


class Session:
    """Represents a user session."""
    
    def __init__(self, session_id: str, user_id: str, metadata: Dict[str, Any] = None):
        """Initialize a session."""
        self.session_id = session_id
        self.user_id = user_id
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.history = []
        
    def add_to_history(self, item: Dict[str, Any]) -> None:
        """Add an item to the session history."""
        self.history.append(item)
        self.last_active = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "history": self.history
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Create session from dictionary."""
        session = cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            metadata=data["metadata"]
        )
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.last_active = datetime.fromisoformat(data["last_active"])
        session.history = data["history"]
        return session


class SessionManager:
    """Manages user sessions."""
    
    def __init__(self, storage_path: str = "sessions"):
        """Initialize session manager."""
        self.storage_path = storage_path
        self.active_sessions = {}
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_path, exist_ok=True)
        
    def create_session(self, user_id: str, metadata: Dict[str, Any] = None) -> Session:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        session = Session(session_id, user_id, metadata)
        self.active_sessions[session_id] = session
        self._save_session(session)
        return session
        
    def load_session(self, session_id: str) -> Optional[Session]:
        """Load a session by ID."""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
            
        session_path = os.path.join(self.storage_path, f"{session_id}.json")
        if os.path.exists(session_path):
            with open(session_path, 'r') as f:
                session_data = json.load(f)
                session = Session.from_dict(session_data)
                self.active_sessions[session_id] = session
                return session
                
        return None
        
    def save_session(self, session: Session) -> None:
        """Save a session."""
        self.active_sessions[session.session_id] = session
        self._save_session(session)
        
    def _save_session(self, session: Session) -> None:
        """Save session to disk."""
        session_path = os.path.join(self.storage_path, f"{session.session_id}.json")
        with open(session_path, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)
            
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            
        session_path = os.path.join(self.storage_path, f"{session_id}.json")
        if os.path.exists(session_path):
            os.remove(session_path)
            return True
            
        return False
        
    def get_all_sessions(self) -> List[Session]:
        """Get all sessions."""
        sessions = list(self.active_sessions.values())
        
        # Load sessions from disk that aren't already loaded
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                session_id = filename[:-5]  # Remove .json extension
                if session_id not in self.active_sessions:
                    session = self.load_session(session_id)
                    if session:
                        sessions.append(session)
                        
        return sessions
