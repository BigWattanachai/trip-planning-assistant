"""
Tavily search tool for retrieving real-time information.
Provides search capabilities for both ADK and direct API modes.
"""
import os
import logging
from typing import Optional, Dict, Any, Union

# Import settings
from config import settings

logger = logging.getLogger(__name__)

def initialize_tavily_search():
    """
    Initialize the Tavily search tool for direct API mode.
    
    Returns:
        A Tavily search tool object or None if initialization fails
    """
    # Check if Tavily API key is set
    tavily_api_key = settings.TAVILY_API_KEY
    if not tavily_api_key:
        logger.warning("TAVILY_API_KEY not set. Search capabilities will be limited.")
        return None
    
    try:
        # Import Tavily search
        from langchain_community.tools.tavily_search import TavilySearchResults
        
        # Set up Tavily search tool
        tavily_search = TavilySearchResults(
            api_key=tavily_api_key,
            max_results=5,
            include_domains=[],
            exclude_domains=[],
            max_characters=4000  # Limit the response size
        )
        
        logger.info("Tavily search tool initialized successfully")
        return tavily_search
    except ImportError as e:
        logger.error(f"Failed to import Tavily search: {e}")
        return None
    except Exception as e:
        logger.error(f"Error initializing Tavily search: {e}")
        return None

def initialize_tavily_search_tool():
    """
    Initialize the Tavily search tool for ADK mode.
    
    Returns:
        A Tavily search tool object or None if initialization fails
    """
    return initialize_tavily_search()

def tavily_search(query: str, search_depth: str = "basic") -> Dict[str, Any]:
    """
    Perform a Tavily search with the given query.
    This is a wrapper around the Tavily search tool for direct API mode.
    
    Args:
        query: The search query
        search_depth: The search depth, either "basic" or "deep"
        
    Returns:
        Search results as a dictionary
    """
    # Initialize Tavily search if needed
    tavily_search_instance = initialize_tavily_search()
    
    if not tavily_search_instance:
        logger.warning(f"Tavily search not available for query: {query}")
        return {"error": "Tavily search not available", "results": []}
    
    try:
        # Call Tavily search
        results = tavily_search_instance.invoke(query, search_depth=search_depth)
        logger.info(f"Tavily search successful for query: {query}")
        
        # For safety and format consistency, convert the results to a dictionary
        if isinstance(results, str):
            # Sometimes Tavily returns a string instead of a dictionary
            results_dict = {"results": [{"content": results}]}
        elif isinstance(results, dict):
            results_dict = results
        elif isinstance(results, list):
            results_dict = {"results": results}
        else:
            results_dict = {"results": [{"content": str(results)}]}
        
        return results_dict
    except Exception as e:
        logger.error(f"Error during Tavily search for query '{query}': {e}")
        return {"error": str(e), "results": []}
