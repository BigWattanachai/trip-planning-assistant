"""
Simple callbacks for ADK agents with basic logging.
These callbacks provide logging of agent requests and responses without complex parsing.
"""

import logging
import json
import time
import os
from typing import Any, Dict, Optional, List

# Configure logging
logger = logging.getLogger(__name__)

# Import ADK components if available
if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes"):
    try:
        from google.adk.agents.callback_context import CallbackContext
        from google.adk.models import LlmRequest, LlmResponse
        from google.adk.tools import ToolContext
        
        # Simple ADK callbacks
        def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> None:
            """Callback that runs before the model is called."""
            try:
                # Log basic information about the request
                logger.info(f"🔍 MODEL REQUEST from root_agent")
                
                # Add timestamp for rate limiting (similar to original rate_limit_callback)
                now = time.time()
                if "timer_start" not in callback_context.state:
                    callback_context.state["timer_start"] = now
                    callback_context.state["request_count"] = 1
                    logger.debug(
                        "before_model_callback [timestamp: %i, req_count: 1, elapsed_secs: 0]",
                        now,
                    )
                    return
                
                request_count = callback_context.state["request_count"] + 1
                elapsed_secs = now - callback_context.state["timer_start"]
                
                # Update context
                callback_context.state["request_count"] = request_count
                
                # Log for debugging
                logger.debug(
                    "before_model_callback [timestamp: %i, req_count: %i, elapsed_secs: %i]",
                    now,
                    request_count,
                    elapsed_secs,
                )
            except Exception as e:
                logger.error(f"Error in before_model_callback: {str(e)}")
        
        def after_model_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> None:
            """Callback that runs after the model is called."""
            try:
                # Log basic information about the response
                logger.info(f"✅ MODEL RESPONSE to root_agent")
            except Exception as e:
                logger.error(f"Error in after_model_callback: {str(e)}")
        
        def before_tool_callback(callback_context: CallbackContext, tool_context: ToolContext) -> None:
            """Callback that runs before a tool is called."""
            try:
                # Get tool name if available
                tool_name = "unknown_tool"
                if hasattr(tool_context, "tool") and hasattr(tool_context.tool, "name"):
                    tool_name = tool_context.tool.name
                
                # Log the tool call
                logger.info(f"🛠️ TOOL CALL: {tool_name}")
            except Exception as e:
                logger.error(f"Error in before_tool_callback: {str(e)}")
        
        def after_tool_callback(callback_context: CallbackContext, tool_context: ToolContext) -> None:
            """Callback that runs after a tool is called."""
            try:
                # Get tool name if available
                tool_name = "unknown_tool"
                if hasattr(tool_context, "tool") and hasattr(tool_context.tool, "name"):
                    tool_name = tool_context.tool.name
                
                # Log the tool response
                logger.info(f"🔄 TOOL RESPONSE: {tool_name}")
            except Exception as e:
                logger.error(f"Error in after_tool_callback: {str(e)}")
            
    except ImportError as e:
        logger.error(f"Failed to import ADK components for simple callbacks: {e}")
        before_model_callback = None
        after_model_callback = None
        before_tool_callback = None
        after_tool_callback = None
else:
    logger.info("Direct API Mode: Simple ADK callbacks not loaded")
    before_model_callback = None
    after_model_callback = None
    before_tool_callback = None
    after_tool_callback = None
