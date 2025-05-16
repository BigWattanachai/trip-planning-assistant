"""
Enhanced callbacks for ADK agents with detailed logging.
These callbacks provide detailed logging of agent requests and responses.

This extends the basic callbacks.py functionality with more detailed logging.
"""

import logging
import json
import time
from typing import Any, Dict, Optional, List

# Configure logging
logger = logging.getLogger(__name__)

def format_content_for_logging(content: Any) -> str:
    """Format content for logging, handling different types and truncating if needed."""
    try:
        if isinstance(content, dict):
            # Convert dict to JSON string with indentation
            formatted = json.dumps(content, indent=2, ensure_ascii=False)
        elif isinstance(content, list):
            # Handle lists
            formatted = json.dumps(content, indent=2, ensure_ascii=False)
        elif isinstance(content, str):
            formatted = content
        else:
            formatted = str(content)

        # Truncate if too long (more than 500 chars)
        if len(formatted) > 500:
            return formatted[:500] + "... [truncated]"
        return formatted
    except Exception as e:
        return f"[Error formatting content: {str(e)}]"

def log_model_request(request: Dict[str, Any], agent_name: str = "unknown") -> None:
    """Log a model request with detailed information."""
    try:
        # Extract key information
        contents = request.get("contents", [])
        tools = request.get("tools", [])

        # Log basic request info
        logger.info(f"[{agent_name}] 🔍 MODEL REQUEST:")

        # Log prompt/contents
        if contents:
            for i, content in enumerate(contents):
                parts = content.get("parts", [])
                for j, part in enumerate(parts):
                    if "text" in part:
                        text = part["text"]
                        # Truncate long text
                        if len(text) > 500:
                            text = text[:500] + "... [truncated]"
                        logger.info(f"[{agent_name}] 📝 PROMPT [{i}][{j}]: {text}")

        # Log tools
        if tools:
            tool_names = [tool.get("function_declarations", {}).get("name", "unknown") for tool in tools]
            logger.info(f"[{agent_name}] 🔧 TOOLS: {', '.join(tool_names)}")

    except Exception as e:
        logger.error(f"[{agent_name}] Error logging model request: {str(e)}")

def log_model_response(response: Dict[str, Any], agent_name: str = "unknown") -> None:
    """Log a model response with detailed information."""
    try:
        # Extract key information
        candidates = response.get("candidates", [])

        # Log basic response info
        logger.info(f"[{agent_name}] ✅ MODEL RESPONSE:")

        # Log content from candidates
        for i, candidate in enumerate(candidates):
            content = candidate.get("content", {})
            parts = content.get("parts", [])

            for j, part in enumerate(parts):
                if "text" in part:
                    text = part["text"]
                    # Truncate long text
                    if len(text) > 500:
                        text = text[:500] + "... [truncated]"
                    logger.info(f"[{agent_name}] 📄 RESPONSE TEXT [{i}][{j}]: {text}")

            # Log function calls
            function_calls = []
            for part in parts:
                if "function_call" in part:
                    function_call = part["function_call"]
                    name = function_call.get("name", "unknown")
                    args = function_call.get("args", {})
                    function_calls.append({"name": name, "args": args})

            if function_calls:
                for k, call in enumerate(function_calls):
                    logger.info(f"[{agent_name}] 🔄 FUNCTION CALL [{i}][{k}]: {call['name']}({format_content_for_logging(call['args'])})")

    except Exception as e:
        logger.error(f"[{agent_name}] Error logging model response: {str(e)}")

def log_tool_call(tool_name: str, args: Dict[str, Any], agent_name: str = "unknown") -> None:
    """Log a tool call with detailed information."""
    try:
        logger.info(f"[{agent_name}] 🛠️ TOOL CALL: {tool_name}")
        logger.info(f"[{agent_name}] 📋 TOOL ARGS: {format_content_for_logging(args)}")
    except Exception as e:
        logger.error(f"[{agent_name}] Error logging tool call: {str(e)}")

def log_tool_response(tool_name: str, response: Any, agent_name: str = "unknown") -> None:
    """Log a tool response with detailed information."""
    try:
        logger.info(f"[{agent_name}] 🔄 TOOL RESPONSE: {tool_name}")
        logger.info(f"[{agent_name}] 📊 TOOL RESULT: {format_content_for_logging(response)}")
    except Exception as e:
        logger.error(f"[{agent_name}] Error logging tool response: {str(e)}")

# Import ADK components if available
import os
if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes"):
    try:
        from google.adk.agents.callback_context import CallbackContext
        from google.adk.models import LlmRequest, LlmResponse
        from google.adk.tools import ToolContext

        # Enhanced ADK callbacks
        def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> None:
            """Callback that runs before the model is called."""
            # Get agent name from context if available
            agent_name = "root_agent"  # Default name since we can't access agent directly

            # Log the request
            log_model_request(llm_request.to_dict(), agent_name)

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

        def after_model_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> None:
            """Callback that runs after the model is called."""
            # Get agent name from context if available
            agent_name = "root_agent"  # Default name since we can't access agent directly

            # Log the response
            log_model_response(llm_response.to_dict(), agent_name)

        def before_tool_callback(callback_context: CallbackContext, tool_context: ToolContext) -> None:
            """Callback that runs before a tool is called."""
            # Get agent name from context if available
            agent_name = "root_agent"  # Default name since we can't access agent directly

            # Get tool name and args
            tool_name = tool_context.tool.name if hasattr(tool_context.tool, "name") else "unknown_tool"
            args = tool_context.args if hasattr(tool_context, "args") else {}

            # Log the tool call
            log_tool_call(tool_name, args, agent_name)

        def after_tool_callback(callback_context: CallbackContext, tool_context: ToolContext) -> None:
            """Callback that runs after a tool is called."""
            # Get agent name from context if available
            agent_name = "root_agent"  # Default name since we can't access agent directly

            # Get tool name and response
            tool_name = tool_context.tool.name if hasattr(tool_context.tool, "name") else "unknown_tool"
            response = tool_context.response if hasattr(tool_context, "response") else None

            # Log the tool response
            log_tool_response(tool_name, response, agent_name)

    except ImportError as e:
        logger.error(f"Failed to import ADK components for enhanced callbacks: {e}")
        before_model_callback = None
        after_model_callback = None
        before_tool_callback = None
        after_tool_callback = None
else:
    logger.info("Direct API Mode: Enhanced ADK callbacks not loaded")
    before_model_callback = None
    after_model_callback = None
    before_tool_callback = None
    after_tool_callback = None
