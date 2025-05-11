#!/usr/bin/env python
"""
Helper script for integrating Tavily with the Travel Agent

This script demonstrates how to use the Tavily search functionality
in the activity agent from the main agent.
"""

import os
import sys
import pathlib
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to allow imports
parent_dir = str(pathlib.Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

def setup_tavily_integration():
    """
    Set up Tavily integration by adding the activity_tavily_search function
    to the backend agent.
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Setting up Tavily integration...")
    
    try:
        # Import the activity_tavily_search function
        try:
            from sub_agents.activity_agent import activity_tavily_search
            if activity_tavily_search is None:
                raise ImportError("activity_tavily_search function is None")
        except ImportError as e:
            logger.error(f"Failed to import activity_tavily_search: {e}")
            return False
        
        # Test the activity_tavily_search function
        logger.info("Testing activity_tavily_search function...")
        try:
            test_result = activity_tavily_search("popular activities in Thailand")
            if test_result:
                logger.info("Tavily search function is working!")
            else:
                logger.warning("Tavily search returned no results")
        except Exception as e:
            logger.error(f"Error testing Tavily search: {e}")
            return False
        
        # Create a wrapper to demonstrate using the search in the agent
        def search_activities(destination, activity_type=None):
            """
            Search for activities in a specific destination.
            
            Args:
                destination (str): The destination to search for
                activity_type (str, optional): The type of activity to search for
            
            Returns:
                dict: Search results
            """
            query = f"best {activity_type if activity_type else 'tourist'} activities"
            return activity_tavily_search(query, location=destination)
        
        # Example usage
        logger.info("\nExample Usage:")
        print("\n" + "-"*50)
        print("EXAMPLE: HOW TO USE TAVILY SEARCH IN YOUR CODE")
        print("-"*50)
        print("from sub_agents.activity_agent import activity_tavily_search")
        print("")
        print("# Simple query")
        print("results = activity_tavily_search('popular beaches')")
        print("")
        print("# Location-specific query")
        print("results = activity_tavily_search('best hiking trails', location='Phuket')")
        print("")
        print("# For activity recommendations in an agent:")
        print("def get_activity_recommendations(destination):")
        print("    return activity_tavily_search('top attractions and activities', location=destination)")
        print("")
        print("# Example use in your agent.py or custom handler:")
        print("if 'find activities' in user_message.lower():")
        print("    destination = extract_destination(user_message)")
        print("    activity_info = activity_tavily_search('tourist activities', location=destination)")
        print("    response = format_activity_results(activity_info)")
        print("-"*50 + "\n")
        
        # Try a real example
        try:
            example_destination = "Bangkok"
            logger.info(f"Trying a real example with destination: {example_destination}")
            results = search_activities(example_destination)
            if results:
                result_text = str(results)
                preview = result_text[:500] + "..." if len(result_text) > 500 else result_text
                logger.info(f"Got results! Preview: {preview}")
                return True
            else:
                logger.warning("No results returned for the example search")
                return False
        except Exception as e:
            logger.error(f"Error in example search: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error setting up Tavily integration: {e}")
        return False

if __name__ == "__main__":
    success = setup_tavily_integration()
    if success:
        print("\n✅ Tavily integration is set up and working correctly!")
        print("You can now use activity_tavily_search in your main agent.")
    else:
        print("\n❌ There was an issue setting up Tavily integration.")
        print("Please check the logs above for more information.")
