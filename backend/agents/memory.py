"""
Custom implementation of memory classes for Google ADK.
This is needed because the current version of Google ADK doesn't have the ShortTermMemory and LongTermMemory classes.
"""
from typing import Any, Dict, List, Optional
import json
import os
import sqlite3


class ShortTermMemory:
    """Simple in-memory storage for short-term memory."""
    
    def __init__(self, capacity: int = 100):
        """Initialize short-term memory with a capacity."""
        self.capacity = capacity
        self.memory = {}
        
    def save(self, key: str, value: Any) -> None:
        """Save a value to memory."""
        if len(self.memory) >= self.capacity and key not in self.memory:
            # Remove oldest item if at capacity
            oldest_key = next(iter(self.memory))
            del self.memory[oldest_key]
        
        self.memory[key] = value
        
    def load(self, key: str) -> Optional[Any]:
        """Load a value from memory."""
        return self.memory.get(key)
        
    def clear(self) -> None:
        """Clear all memory."""
        self.memory.clear()


class LongTermMemory:
    """Persistent storage for long-term memory using SQLite."""
    
    def __init__(self, storage_backend: str = "sqlite", db_path: str = "memory.db"):
        """Initialize long-term memory with a storage backend."""
        self.storage_backend = storage_backend
        self.db_path = db_path
        
        if storage_backend == "sqlite":
            self._init_sqlite()
        else:
            raise ValueError(f"Unsupported storage backend: {storage_backend}")
        
    def _init_sqlite(self) -> None:
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory (
            key TEXT PRIMARY KEY,
            value TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        conn.close()
        
    def save(self, key: str, value: Any) -> None:
        """Save a value to memory."""
        if self.storage_backend == "sqlite":
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            serialized_value = json.dumps(value)
            cursor.execute(
                "INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)",
                (key, serialized_value)
            )
            conn.commit()
            conn.close()
        
    def load(self, key: str) -> Optional[Any]:
        """Load a value from memory."""
        if self.storage_backend == "sqlite":
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM memory WHERE key = ?", (key,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
        
        return None
        
    def clear(self) -> None:
        """Clear all memory."""
        if self.storage_backend == "sqlite":
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memory")
            conn.commit()
            conn.close()
