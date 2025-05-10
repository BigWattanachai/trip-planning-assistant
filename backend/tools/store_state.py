"""'store_state' tool for Travel Agent"""

import logging
import typing
import os
import sys
import pathlib

# Configure logging
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to allow imports
parent_dir = str(pathlib.Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Only import ADK components if we're using Vertex AI
if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes"):
    try:
        from google.adk.tools import ToolContext

        def store_state_tool(
            state: dict[str, typing.Any], tool_context: ToolContext
        ) -> dict[str, str]:
            """Stores new state values in the ToolContext.

            Args:
              state: A dict of new state values.
              tool_context: ToolContext object.

            Returns:
              A dict with "status" and (optional) "error_message" keys.
            """
            logger.info("store_state_tool(): %s", state)
            tool_context.state.update(state)
            return {"status": "ok"}

        store_state_tool.description = "Store state values in the ToolContext."
        
    except ImportError as e:
        logger.error(f"Failed to import ADK components for store_state_tool: {e}")
        store_state_tool = None
else:
    logger.info("Direct API Mode: store_state_tool not loaded")
    store_state_tool = None
