"""
Tavily search integration for the Travel Agent Backend.
Provides real-time search capabilities for enhancing agent responses.
"""
import os
import logging
import json
from typing import Any, Dict, List, Optional, Union
import requests

from config import settings

logger = logging.getLogger(__name__)

def tavily_search(query: str, search_depth: str = "basic", max_results: int = 5) -> Dict[str, Any]:
    """
    Perform a search using the Tavily Search API.
    
    Args:
        query: The search query
        search_depth: The depth of the search ("basic" or "advanced")
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary containing search results or error message
    """
    api_key = settings.TAVILY_API_KEY
    if not api_key:
        logger.error("TAVILY_API_KEY not set. Cannot perform search.")
        return {"error": "TAVILY_API_KEY not set"}
    
    try:
        logger.info(f"Performing Tavily search for: {query}")
        
        # Prepare the request
        url = "https://api.tavily.com/search"
        headers = {
            "content-type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_answer": True,
            "include_domains": [],
            "exclude_domains": []
        }
        
        # Make the request
        response = requests.post(url, json=payload, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Tavily search successful. Found {len(result.get('results', []))} results.")
            return result
        else:
            logger.error(f"Tavily search failed with status code {response.status_code}: {response.text}")
            return {"error": f"Search failed with status code {response.status_code}"}
    
    except Exception as e:
        logger.error(f"Error performing Tavily search: {e}")
        return {"error": str(e)}

def tavily_search_with_tool_context(query: str, search_depth: str = "basic", max_results: int = 5, tool_context=None) -> Dict[str, Any]:
    """
    Perform a search using the Tavily Search API with ADK ToolContext support.
    
    Args:
        query: The search query
        search_depth: The depth of the search ("basic" or "advanced")
        max_results: Maximum number of results to return
        tool_context: ToolContext object (provided automatically by ADK)
        
    Returns:
        Dictionary containing search results or error message
    """
    # Perform the search
    result = tavily_search(query, search_depth, max_results)
    
    # Store the result in the tool context if available
    if tool_context and "error" not in result:
        # Store the search query and results in the session state
        tool_context.state["last_search_query"] = query
        tool_context.state["last_search_results"] = result
        logger.info(f"Stored Tavily search results in session state for query: {query}")
    
    return result
