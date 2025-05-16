"""
Enhanced callbacks for ADK agents with detailed logging.
These callbacks provide detailed logging of agent requests and responses.
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

# Enhanced ADK callbacks
def before_model_callback(request: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Callback that runs before the model is called."""
    # Get agent name from context if available
    agent_name = context.get("agent_name", "unknown")
    
    # Log the request
    log_model_request(request, agent_name)
    
    # Add timestamp for rate limiting
    timestamp = int(time.time())
    req_count = context.get("req_count", 0) + 1
    elapsed_secs = timestamp - context.get("timestamp", timestamp)
    
    # Update context
    context["timestamp"] = timestamp
    context["req_count"] = req_count
    
    # Log for debugging
    logger.debug(f"before_model_callback [timestamp: {timestamp}, req_count: {req_count}, elapsed_secs: {elapsed_secs}]")
    
    return request

def after_model_callback(response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Callback that runs after the model is called."""
    # Get agent name from context if available
    agent_name = context.get("agent_name", "unknown")
    
    # Log the response
    log_model_response(response, agent_name)
    
    return response

def before_tool_callback(tool_name: str, args: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Callback that runs before a tool is called."""
    # Get agent name from context if available
    agent_name = context.get("agent_name", "unknown")
    
    # Log the tool call
    log_tool_call(tool_name, args, agent_name)
    
    return args

def after_tool_callback(tool_name: str, response: Any, context: Dict[str, Any]) -> Any:
    """Callback that runs after a tool is called."""
    # Get agent name from context if available
    agent_name = context.get("agent_name", "unknown")
    
    # Log the tool response
    log_tool_response(tool_name, response, agent_name)
    
    return response
