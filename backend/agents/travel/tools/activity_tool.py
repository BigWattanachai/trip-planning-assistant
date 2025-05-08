"""
Activity Tool: A tool for the root agent to call the activity agent.
"""
from typing import Dict, Any
from google.adk.tools import Tool
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Part, Content

# Import the activity agent
from backend.agents.activity.activity_search_agent import activity_search_agent

class ActivityTool(Tool):
    """A tool for the root agent to call the activity agent."""

    def __init__(self):
        """Initialize the activity tool."""
        super().__init__(
            name="activity_agent",
            description="Use this tool when the user asks about activities, attractions, or things to do in a destination.",
            parameters={
                "query": {
                    "type": "string",
                    "description": "The user's query about activities or attractions."
                },
                "context": {
                    "type": "string",
                    "description": "Additional context information that might be helpful for the activity agent."
                }
            },
            returns={
                "response": {
                    "type": "string",
                    "description": "The activity agent's response to the user's query."
                }
            }
        )
        # Create a session service and runner for the activity agent
        self.session_service = InMemorySessionService()
        self.runner = Runner(agent=activity_search_agent, app_name="Travel Planning Assistant", session_service=self.session_service)
        # Create a session
        self.session_service.create_session(app_name="Travel Planning Assistant", user_id="user_123", session_id="activity_session")

    def execute(self, query: str, context: str = "") -> Dict[str, Any]:
        """
        Execute the activity tool by calling the activity agent.

        Args:
            query: The user's query about activities or attractions.
            context: Additional context information that might be helpful for the activity agent.

        Returns:
            A dictionary containing the activity agent's response.
        """
        # Combine the query and context
        enhanced_query = query
        if context:
            enhanced_query = f"{context}\n\n{query}"

        # Create content object for the agent
        content = Content(role="user", parts=[Part(text=enhanced_query)])

        # Call the activity agent
        response = self.runner.run(user_id="user_123", session_id="activity_session", new_message=content)

        # Extract the response text
        response_text = ""
        if response and hasattr(response, "content") and hasattr(response.content, "parts") and len(response.content.parts) > 0:
            response_text = response.content.parts[0].text

        return {"response": response_text}

# Create an instance of the activity tool
activity_tool = ActivityTool()