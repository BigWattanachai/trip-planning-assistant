"""
Configuration settings for the Travel Agent application.
Uses Pydantic's settings management to handle environment variables.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Core settings
    APP_NAME: str = "Travel Planning Assistant"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    ENV: str = "development"
    
    # Google AI settings
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_GENAI_MODEL: str = "gemini-2.0-flash"
    GOOGLE_GENAI_USE_VERTEXAI: bool = False
    
    # Search API settings
    TAVILY_API_KEY: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None
    
    # Session state settings
    DEFAULT_LANGUAGE: str = "th"
    DEFAULT_CURRENCY: str = "THB"
    SESSION_STORAGE_TYPE: str = "memory"  # Options: memory, redis, firestore
    SESSION_STORAGE_URL: Optional[str] = None
    
    # Runtime properties
    USE_VERTEX_AI: bool = False  # Will be set based on GOOGLE_GENAI_USE_VERTEXAI
    MODEL: str = ""              # Will be set based on GOOGLE_GENAI_MODEL
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Convert string to bool for USE_VERTEX_AI
        self.USE_VERTEX_AI = self.GOOGLE_GENAI_USE_VERTEXAI
        # Use the model name directly
        self.MODEL = self.GOOGLE_GENAI_MODEL
        
        # Check API keys and log warnings
        if not self.GOOGLE_API_KEY and not self.USE_VERTEX_AI:
            import logging
            logging.getLogger(__name__).warning("GOOGLE_API_KEY not set. Direct API mode may not work.")
        
        if not self.TAVILY_API_KEY:
            import logging
            logging.getLogger(__name__).warning("TAVILY_API_KEY environment variable is not set.")
        else:
            import logging
            logging.getLogger(__name__).info(f"TAVILY_API_KEY is set with length {len(self.TAVILY_API_KEY)}")

# Create a global instance of settings
settings = Settings()
