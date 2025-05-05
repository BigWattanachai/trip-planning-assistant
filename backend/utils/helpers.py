import os
import json
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
import re
import asyncio
from functools import wraps

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sanitize_input(text: str) -> str:
    """
    Remove potentially harmful characters from input
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove SQL injection patterns
    text = re.sub(r'(\b(select|insert|update|delete|from|where|drop|create|alter)\b)', 
                 lambda match: match.group(1).capitalize(), 
                 text, 
                 flags=re.IGNORECASE)
    
    # Remove script patterns
    text = re.sub(r'(\b(script|javascript|eval|document\.cookie)\b)', 
                 lambda match: match.group(1).capitalize(), 
                 text, 
                 flags=re.IGNORECASE)
    
    return text

def validate_dates(start_date: str, end_date: str) -> bool:
    """
    Validate date format and ranges
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Check if end date is after start date
        if end <= start:
            return False
        
        # Check if dates are too far in the future (e.g., 1 year)
        if start > datetime.now() + timedelta(days=365):
            return False
        
        return True
    except ValueError:
        return False

def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency amounts with appropriate symbols
    """
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "THB": "฿",
        "CNY": "¥",
        "KRW": "₩",
        "INR": "₹"
    }
    
    symbol = currency_symbols.get(currency, currency)
    
    # Format with commas and 2 decimal places
    if currency in ["JPY", "KRW"]:
        # No decimal places for these currencies
        formatted = f"{symbol}{int(amount):,}"
    else:
        formatted = f"{symbol}{amount:,.2f}"
    
    return formatted

def calculate_trip_duration(start_date: str, end_date: str) -> int:
    """
    Calculate the duration of a trip in days
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    delta = end - start
    
    return delta.days

def extract_keywords(text: str) -> List[str]:
    """
    Extract keywords from text for better search results
    """
    # Remove common stop words
    stop_words = {"and", "or", "the", "a", "an", "in", "on", "at", "to", "for", "with", "by", "about", "like"}
    
    # Split text into words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter out stop words and short words
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Get unique keywords
    unique_keywords = list(set(keywords))
    
    # Return top keywords (up to 10)
    return unique_keywords[:10]

def retry_async(max_retries=3, delay=1, backoff_factor=2):
    """
    Decorator for retrying async functions
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Failed after {max_retries} retries: {str(e)}")
                        raise
                    
                    logger.warning(f"Retry {retries}/{max_retries} after error: {str(e)}")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff_factor
            
            # Should not reach here, but just in case
            raise Exception(f"Failed after {max_retries} retries")
        
        return wrapper
    
    return decorator

def parse_duration(duration_str: str) -> int:
    """
    Parse duration string (e.g., "5h 30m") to minutes
    """
    hours = 0
    minutes = 0
    
    # Extract hours
    hour_match = re.search(r'(\d+)h', duration_str)
    if hour_match:
        hours = int(hour_match.group(1))
    
    # Extract minutes
    minute_match = re.search(r'(\d+)m', duration_str)
    if minute_match:
        minutes = int(minute_match.group(1))
    
    # Convert to total minutes
    return hours * 60 + minutes

def get_destination_country(destination: str) -> str:
    """
    Try to extract country from destination
    This is a simple implementation - in a real app, use a proper geo database
    """
    # Check if destination has comma (e.g., "Bangkok, Thailand")
    if "," in destination:
        parts = destination.split(",")
        return parts[-1].strip()
    
    return destination
