#!/usr/bin/env python
"""
Test script for Tavily API integration
"""

import os
import sys
import pathlib

# Add the parent directory to sys.path to allow imports
parent_dir = str(pathlib.Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# First, check if TAVILY_API_KEY is set
tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    print("WARNING: TAVILY_API_KEY environment variable is not set.")
    print("To use Tavily, please set this variable by adding it to your .env file:")
    print("TAVILY_API_KEY=your_api_key_here")
    sys.exit(1)

print(f"TAVILY_API_KEY is set: {tavily_api_key[:4]}{'*' * (len(tavily_api_key) - 8)}{tavily_api_key[-4:]}")

try:
    print("Attempting to import TavilySearchResults...")
    from langchain_community.tools import TavilySearchResults
    print("Successfully imported TavilySearchResults")
    
    # Initialize Tavily search tool
    print("Initializing Tavily search tool...")
    tavily_search = TavilySearchResults(
        max_results=5,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True,
        include_images=True,
    )
    print("Successfully created Tavily search instance")
    
    # Test a search
    print("Testing a search for 'travel to thailand'...")
    result = tavily_search.invoke("travel to thailand")
    print("Search successful!")
    print("Result type:", type(result))
    print("Result:", result[:500], "..." if len(str(result)) > 500 else "")
    
    print("\nTavily integration is working correctly!")
    
except ImportError as e:
    print(f"Failed to import TavilySearchResults: {e}")
    print("Please ensure you've installed the required dependencies:")
    print("pip install langchain>=0.1.0 langchain-community>=0.1.0 tavily-python>=0.2.8")
    sys.exit(1)
except Exception as e:
    print(f"Error testing Tavily search: {e}")
    sys.exit(1)
