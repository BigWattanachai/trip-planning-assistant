import os
import logging

logger = logging.getLogger(__name__)

def initialize_tavily_search():
    """Initialize the Tavily search tool and return it if successful."""
    print("Starting Tavily search tool initialization")
    logger.info("Starting Tavily search tool initialization")

    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        print("WARNING: TAVILY_API_KEY environment variable not set. Tavily search tool will not function properly.")
        logger.warning("TAVILY_API_KEY environment variable not set. Tavily search tool will not function properly.")
        return None
    else:
        print(f"Found Tavily API key: {tavily_api_key[:4]}{'*' * (len(tavily_api_key) - 8)}{tavily_api_key[-4:]}")
        logger.info(f"Found Tavily API key with length {len(tavily_api_key)}")

    try:
        from langchain_community.tools import TavilySearchResults
        from tavily import TavilyClient
        print("Successfully imported TavilySearchResults and TavilyClient")
        logger.info("Successfully imported TavilySearchResults and TavilyClient")
        try:
            client = TavilyClient(api_key=tavily_api_key)
            print("Created TavilyClient successfully")
            logger.info("Created TavilyClient successfully")
        except Exception as e:
            print(f"Error creating TavilyClient: {e}")
            logger.error(f"Error creating TavilyClient: {e}")
            return None
        tavily_search = TavilySearchResults(
            max_results=5,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=True,
            include_images=True,
        )
        print("Successfully created Tavily search instance")
        logger.info("Successfully created Tavily search instance")
        try:
            print("Testing Tavily search with a sample query...")
            logger.info("Testing Tavily search with a sample query...")
            test_result = tavily_search.invoke("travel to Thailand attractions")
            if test_result:
                print("Test query successful!")
                logger.info("Test query successful!")
            else:
                print("Test query returned no results")
                logger.warning("Test query returned no results")
        except Exception as e:
            print(f"Error testing Tavily search: {e}")
            logger.error(f"Error testing Tavily search: {e}")
        return tavily_search
    except ImportError as e:
        print(f"Failed to import Tavily dependencies: {e}")
        logger.error(f"Failed to import Tavily dependencies: {e}")
        print("Please install the required packages: pip install langchain>=0.1.0 langchain-community>=0.1.0 tavily-python>=0.2.8")
        return None
    except Exception as e:
        print(f"Unexpected error initializing Tavily search: {e}")
        logger.error(f"Unexpected error initializing Tavily search: {e}")
        return None

def get_tavily_tool_instance():
    """Returns a ready-to-use Tavily search instance, or None if not available."""
    return initialize_tavily_search()
