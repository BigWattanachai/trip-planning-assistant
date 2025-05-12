"""
Root agent module for Travel Agent Backend.
Handles the creation and configuration of the root agent that coordinates sub-agents.
Supports both Vertex AI (ADK) and direct API modes.
"""
import os
import logging
from typing import Any, Dict, List, Optional, Union

from config import settings
from services.session import initialize_adk_session_service
from agent.prompts.root_agent_prompt import ROOT_AGENT_PROMPT
from agent.tools.extract_info import extract_travel_info
from agent.utils.callbacks import rate_limit_callback, sensitive_info_filter_callback

logger = logging.getLogger(__name__)

# Global variables to store agent-related resources
_root_agent = None
_adk_app = None
_adk_session_service = None
_all_sub_agents = {}

def initialize_agents() -> bool:
    """
    Initialize all agent-related resources based on the current mode.
    This should be called once at application startup.
    
    Returns:
        bool: True if initialization was successful, False otherwise
    """
    # Configure the Google Generative AI client if we're not in Vertex AI mode
    if not settings.USE_VERTEX_AI:
        try:
            import google.generativeai as genai
            
            api_key = settings.GOOGLE_API_KEY
            if api_key:
                logger.info("Configuring Gemini API with provided key")
                genai.configure(api_key=api_key)
            else:
                logger.warning("GOOGLE_API_KEY not set. Direct API mode may not work.")
        except ImportError as e:
            logger.error(f"Failed to import Google Generative AI: {e}")
            return False
            
    # Load sub-agents
    sub_agents = _initialize_sub_agents()
    if sub_agents or not settings.USE_VERTEX_AI:
        # In direct API mode, we don't need sub-agents to be loaded
        return True
    else:
        return False

def _initialize_sub_agents() -> Dict[str, Any]:
    """
    Initialize all sub-agents.
    Called during application startup.
    
    Returns:
        Dictionary mapping agent types to agent objects
    """
    global _all_sub_agents
    
    # Import sub-agents differently based on mode
    if settings.USE_VERTEX_AI:
        try:
            # Import the sub-agents module
            from agent.sub_agents import initialize_sub_agents
            
            # Initialize the sub-agents
            _all_sub_agents = initialize_sub_agents()
            
            logger.info(f"Initialized {len(_all_sub_agents)} ADK sub-agents")
            return _all_sub_agents
        except ImportError as e:
            logger.error(f"Failed to import sub-agents module: {e}")
            return {}
    else:
        # In direct API mode, we don't need to preload anything, 
        # as direct mode uses function calls
        logger.info("Direct API Mode: No sub-agents preloaded")
        return {}

def create_root_agent() -> Any:
    """
    Create and configure the root agent based on the current mode.
    
    Returns:
        The root agent object (either an ADK Agent in Vertex AI mode, 
        or None in direct API mode since it uses function calls)
    """
    global _root_agent, _adk_app, _adk_session_service
    
    if settings.USE_VERTEX_AI:
        try:
            # Import ADK components
            import warnings
            from google.adk.agents import Agent
            from google.adk.tools import ToolContext
            from google.adk.sessions import InMemorySessionService
            
            warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")
            
            # Import tools
            from agent.tools.store_state import store_state_tool
            
            # Create session service
            _adk_session_service = InMemorySessionService()
            # Make the session service available to our session manager
            initialize_adk_session_service(_adk_session_service)
            
            # Simple tool to extract travel information
            def extract_info_tool(query: str, tool_context: ToolContext) -> Dict:
                """Extracts travel information from the query and stores it in the ToolContext state."""
                logger.info(f"Extracting travel info from: {query[:50]}...")
                travel_info = extract_travel_info(query)
                logger.info(f"Extracted travel info: {travel_info}")
                # Update the tool context state
                tool_context.state.update(travel_info)
                return {"status": "ok", "info": travel_info}
            
            extract_info_tool.description = "Extract travel information from the query and store it in the state."
            
            # Get the list of sub-agents
            sub_agent_list = list(_all_sub_agents.values())
            if not sub_agent_list:
                logger.warning("No sub-agents available. Root agent will have limited functionality.")
            
            # Create the root agent with all sub-agents
            _root_agent = Agent(
                model=settings.MODEL,
                name="root_agent",
                description="Travel planning agent that creates comprehensive travel plans",
                instruction=ROOT_AGENT_PROMPT,
                tools=[store_state_tool, extract_info_tool],
                sub_agents=sub_agent_list,
                before_model_callback=sensitive_info_filter_callback,
                output_key="last_response"  # Store the agent's response
            )
            
            # Initialize the ADK App if needed
            try:
                from vertexai.preview.reasoning_engines import AdkApp
                _adk_app = AdkApp(agent=_root_agent, enable_tracing=True)
                logger.info("ADK App initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize ADK App: {e}")
                _adk_app = None
                
            logger.info("Root agent created with ADK")
            return _root_agent
            
        except ImportError as e:
            logger.error(f"Failed to import ADK components: {e}")
            return None
    else:
        # In direct API mode, we don't create an ADK agent
        # Instead, we use the agent_handler module to call sub-agents directly
        logger.info("Direct API Mode: Using function-based agent handler")
        return None

def get_root_agent() -> Any:
    """Get the current root agent instance."""
    return _root_agent

def get_adk_app() -> Any:
    """Get the current ADK App instance."""
    return _adk_app

def get_adk_session_service() -> Any:
    """Get the current ADK session service."""
    return _adk_session_service
