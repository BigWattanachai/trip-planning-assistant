"""
Tavily Search Integration for Travel A2A Application
This module provides search capabilities via the Tavily Search API for all agents.
"""

import os
import logging
from typing import Optional, Dict, Any, Union

# Configure logging
logger = logging.getLogger(__name__)

def initialize_tavily_search():
    """
    Initialize the Tavily search tool and return it if successful.
    
    Returns:
        TavilySearchResults or None: The initialized search tool or None if failed
    """
    logger.info("Starting Tavily search tool initialization")
    print("Starting Tavily search tool initialization")

    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        logger.warning("TAVILY_API_KEY environment variable not set. Tavily search tool will not function properly.")
        print("WARNING: TAVILY_API_KEY environment variable not set. Tavily search tool will not function properly.")
        return None
    else:
        logger.info(f"Found Tavily API key with length {len(tavily_api_key)}")
        print(f"Found Tavily API key: {tavily_api_key[:4]}{'*' * (len(tavily_api_key) - 8)}{tavily_api_key[-4:]}")

    try:
        from langchain_community.tools import TavilySearchResults
        logger.info("Successfully imported TavilySearchResults")
        print("Successfully imported TavilySearchResults")
        
        tavily_search = TavilySearchResults(
            max_results=5,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=True,
            include_images=True,
        )
        logger.info("Successfully created Tavily search instance")
        print("Successfully created Tavily search instance")
        try:
            # Test search with a simple query
            logger.info("Testing Tavily search with a sample query...")
            print("Testing Tavily search with a sample query...")
            test_result = tavily_search.invoke("travel to thailand attractions")
            
            if test_result:
                logger.info("Tavily test query successful!")
                print("Tavily test query successful!")
            else:
                logger.warning("Tavily test query returned no results")
                print("Tavily test query returned no results")
        except Exception as e:
            logger.error(f"Error testing Tavily search: {e}")
            print(f"Error testing Tavily search: {e}")
        
        return tavily_search
    except ImportError as e:
        logger.error(f"Failed to import Tavily dependencies: {e}")
        print(f"Failed to import Tavily dependencies: {e}")
        print("Please install the required packages: pip install langchain>=0.1.0 langchain-community>=0.1.0 tavily-python>=0.2.8")
        return None
    except Exception as e:
        logger.error(f"Unexpected error initializing Tavily search: {e}")
        print(f"Unexpected error initializing Tavily search: {e}")
        return None

def get_tavily_tool_instance():
    """Returns a ready-to-use Tavily search instance, or None if not available."""
    return initialize_tavily_search()

def search_with_tavily(query: str, location: Optional[str] = None, max_results: int = 5) -> Dict[str, Any]:
    """
    Search for information using Tavily search.
    
    Args:
        query: The search query
        location: Optional location to focus the search on
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        dict: Search results or None if search failed
    """
    # Log beginning of search operation with detailed parameters
    logger.info(f"=== TAVILY SEARCH START ===")
    logger.info(f"Query: {query}")
    logger.info(f"Location: {location if location else 'Not specified'}")
    logger.info(f"Max results: {max_results}")
    
    tavily_search = get_tavily_tool_instance()
    
    if not tavily_search:
        error_msg = "Tavily search tool not available for query: " + query
        logger.error(error_msg)
        return {"error": error_msg, "success": False}
    
    try:
        # Add location context if provided
        search_query = query
        if location and location.strip():
            # Check if location is already in query to avoid duplication
            if location.lower() not in query.lower():
                search_query = f"{query} in {location}"
        
        logger.info(f"Formatted search query: {search_query}")
        
        # Additional debug logging for API key verification
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            error_msg = "CRITICAL ERROR: TAVILY_API_KEY is not set in environment variables"
            logger.error(error_msg)
            return {"error": "Tavily API key not configured", "success": False}
        else:
            logger.info(f"Using Tavily API key (masked): {tavily_api_key[:4]}...{tavily_api_key[-4:]} (length: {len(tavily_api_key)})")
        
        # Set dynamic parameters (max_results) if different from default
        if max_results != 5:
            logger.info(f"Creating custom Tavily search instance with max_results={max_results}")
            # Need to recreate the tool with new parameters
            from langchain_community.tools import TavilySearchResults
            tavily_search = TavilySearchResults(
                max_results=max_results,
                search_depth="advanced",
                include_answer=True,
                include_raw_content=True,
                include_images=True,
            )
        
        # Execute search with detailed logging
        logger.info(f"Executing Tavily search invoke() for query: '{search_query}'")
        
        try:
            # Invoke the search and time it
            import time
            start_time = time.time()
            result = tavily_search.invoke(search_query)
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"Tavily search completed in {duration:.2f} seconds")
            logger.info(f"Raw Tavily response type: {type(result)}")
            
            # For ADK diagnostic purposes, log the complete result structure
            import json
            try:
                # Log sample of the response for debugging
                if isinstance(result, dict):
                    logger.info(f"Tavily response keys: {result.keys()}")
                    # Limit the log size to avoid excessively large logs
                    compact_result = {k: v for k, v in result.items() if k != 'raw_content'}
                    logger.info(f"Tavily response structure: {json.dumps(compact_result)[:1000]}...(truncated)")
                elif isinstance(result, list):
                    logger.info(f"Tavily returned a list with {len(result)} items")
                    if result:
                        # Log the first item if available
                        sample_item = result[0]
                        if isinstance(sample_item, dict):
                            logger.info(f"First result keys: {sample_item.keys()}")
                            logger.info(f"First result sample: {json.dumps(sample_item)[:1000]}...(truncated)")
                        else:
                            logger.info(f"First result (non-dict): {str(sample_item)[:200]}")
                else:
                    logger.info(f"Unexpected result type: {type(result)}")
            except Exception as json_error:
                logger.error(f"Error logging Tavily response: {json_error}")
        except Exception as search_error:
            error_msg = f"Exception during Tavily search execution: {str(search_error)}"
            logger.error(error_msg)
            logger.error(f"Error type: {type(search_error).__name__}")
            raise
        
        # Format results for easier consumption
        formatted_result = {
            "query": search_query,
            "success": True,
            "results": []
        }
        
        # Process response based on its type (list or dictionary)
        if isinstance(result, list):
            logger.info(f"Processing Tavily list response with {len(result)} items")
            
            # Direct list of results - process each item
            for item in result:
                if isinstance(item, dict):
                    formatted_item = {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("content", "")
                    }
                    formatted_result["results"].append(formatted_item)
                    logger.info(f"Added result from list: {formatted_item['title']} ({formatted_item['url']})")
        
        elif isinstance(result, dict):
            # Extract answer if available (dictionary format)
            if "answer" in result and result["answer"]:
                formatted_result["answer"] = result["answer"]
                logger.info(f"Tavily provided answer: {result['answer'][:100]}...(truncated)")
            
            # Format search results from dictionary format
            if "results" in result:
                for item in result["results"]:
                    formatted_item = {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("content", "")
                    }
                    formatted_result["results"].append(formatted_item)
                    logger.info(f"Added result from dict: {formatted_item['title']} ({formatted_item['url']})")
        
        # Better success/failure logging based on actual results
        result_count = len(formatted_result['results'])
        if result_count > 0:
            logger.info(f"Tavily search SUCCESS for '{search_query}'. Found {result_count} results.")
        else:
            logger.warning(f"Tavily search completed but found NO RESULTS for '{search_query}'")
            # Add answer even when no results to provide some value
            if 'answer' not in formatted_result or not formatted_result['answer']:
                formatted_result['answer'] = f"No specific information found for {search_query}. Try modifying your search query."
                logger.info(f"Added default answer for empty results: {formatted_result['answer']}")
        
        logger.info(f"=== TAVILY SEARCH COMPLETE ===")
        return formatted_result
        
    except Exception as e:
        error_details = str(e)
        logger.error(f"Error in Tavily search for '{query}': {error_details}")
        logger.error(f"Exception type: {type(e).__name__}")
        
        # Provide more specific error message based on exception type
        error_message = "Search failed"
        if "authorization" in error_details.lower() or "api key" in error_details.lower():
            error_message = "Authentication failed - please check your Tavily API key"
        elif "timeout" in error_details.lower() or "connection" in error_details.lower():
            error_message = "Connection error - please check your internet connection"
        elif "session" in error_details.lower() and "not found" in error_details.lower():
            error_message = "Session not found - this may be an ADK session issue"
            logger.error("This appears to be an ADK session issue. Check if your ADK runner and session service are properly configured.")
        
        result = {
            "error": error_message,
            "error_details": error_details,
            "success": False,
            "query": query,
            "results": []
        }
        
        logger.error(f"=== TAVILY SEARCH FAILED ===")
        import json
        logger.error(json.dumps(result))
        return result

def format_tavily_results_for_agent(results: Dict[str, Any]) -> str:
    """
    Format Tavily search results into a readable string for agents.
    
    Args:
        results: The Tavily search results dictionary
        
    Returns:
        str: Formatted search results as text
    """
    if not results or not isinstance(results, dict):
        return "ไม่พบข้อมูลจากการค้นหา"
    
    if not results.get("success", False):
        error_msg = results.get("error", "ไม่ทราบสาเหตุ")
        return f"การค้นหาล้มเหลว: {error_msg}"
    
    formatted_text = f"ผลการค้นหาสำหรับ '{results.get('query', '')}'\n\n"
    
    # Include the direct answer if available
    if "answer" in results and results["answer"]:
        formatted_text += f"คำตอบโดยตรง: {results['answer']}\n\n"
    
    # Include search results
    if "results" in results and results["results"]:
        formatted_text += "ผลการค้นหา:\n"
        for i, result in enumerate(results["results"], 1):
            formatted_text += f"{i}. {result.get('title', 'ไม่มีชื่อ')}\n"
            formatted_text += f"   URL: {result.get('url', '')}\n"
            content = result.get('content', '')
            if content:
                # Truncate long content
                if len(content) > 300:
                    content = content[:297] + "..."
                formatted_text += f"   สรุป: {content}\n\n"
    else:
        formatted_text += "ไม่พบผลลัพธ์ที่เกี่ยวข้อง"
    
    return formatted_text
