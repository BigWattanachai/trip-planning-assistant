import os
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

class Settings(BaseSettings):
    """Application settings."""
    
    # App settings
    APP_NAME: str = "Travel Planner API"
    API_PREFIX: str = "/api"
    DEBUG: bool = True
    VERSION: str = "0.1.0"
    
    # Model settings
    DEFAULT_MODEL: str = "gemini-1.5-flash"
    COORDINATOR_MODEL: str = "gemini-1.5-pro"
    MODEL_TIMEOUT: int = 60  # seconds
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    
    # Gemnini API settings
    GOOGLE_API_KEY: Optional[str] = None
    
    # Cache settings
    ENABLE_CACHE: bool = True
    CACHE_TTL: int = 3600  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create global settings object
settings = Settings()
