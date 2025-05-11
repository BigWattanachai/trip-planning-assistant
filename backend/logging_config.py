"""
Logging configuration for the Travel A2A backend
"""

import logging
import sys

def configure_logging(level=logging.INFO):
    """
    Configure logging for the application
    """
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Create console handler with a higher log level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    root_logger.addHandler(console_handler)
    
    # Create file handler which logs even debug messages
    try:
        file_handler = logging.FileHandler('tavily_debug.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Could not create log file: {e}")
    
    # Configure specific loggers
    logging.getLogger('sub_agents.activity_agent').setLevel(logging.DEBUG)
    
    return root_logger

# Configure logging when module is imported
logger = configure_logging()
