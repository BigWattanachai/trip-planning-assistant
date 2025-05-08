"""
Improved Agent Orchestrator: A module that coordinates between multiple agents
"""
import sys
import pathlib
from typing import Dict, List, Any, Optional, Tuple, AsyncGenerator
from google.adk.runners import Runner
from google.genai.types import Part, Content

# Handle imports for both running as a module and running directly
try:
    # When running as a module (python -m backend.main)
    from .state_manager import state_manager
    from ..agents.travel_agent import root_agent
    from ..agents.activity_search_agent import activity_search_agent
    from ..agents.restaurant_agent import restaurant_agent
    from ..utils.agent_instructions import get_instructions_for_agent
except (ImportError, ValueError):
    # When running directly (python main.py)
    # Add the parent directory to sys.path
    parent_dir = str(pathlib.Path(__file__).parent.parent.parent.absolute())
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)

    # Use absolute imports
    from backend.core.state_manager import state_manager
    from backend.agents.travel_agent import root_agent
    from backend.agents.activity_search_agent import activity_search_agent
    from backend.agents.restaurant_agent import restaurant_agent
    from backend.utils.agent_instructions import get_instructions_for_agent

class ImprovedAgentOrchestrator:
    """
    Orchestrates requests between multiple specialized agents with enhanced state management.

    This class manages the flow of information between different agents,
    ensuring that user queries are sent to the appropriate agent while
    maintaining rich conversation context and state.
    """

    def __init__(self):
        """Initialize the improved agent orchestrator"""
        # Map of agent types to agent instances
        self.agents = {
            "travel": root_agent,
            "activity": activity_search_agent,
            "restaurant": restaurant_agent
        }

    def classify_intent(self, user_message: str, session_id: str) -> str:
        """
        Determine which agent should handle the user message.

        Args:
            user_message: The user's message
            session_id: Session identifier

        Returns:
            String identifying the agent type that should handle the request
        """
        # Handle imports for both running as a module and running directly
        try:
            # When running as a module (python -m backend.main)
            from ..agents.travel_agent import classify_intent
        except (ImportError, ValueError):
            # When running directly (python main.py)
            from backend.agents.travel_agent import classify_intent

        # First, check if this is a follow-up question
        if state_manager.is_follow_up_question(session_id, user_message):
            # Get the previous agent type
            previous_agent = state_manager.get_state(session_id).get("current_agent")
            if previous_agent and previous_agent != "travel":
                return previous_agent

        # Use the intent classifier with additional context
        agent_type = classify_intent(user_message)

        # Update the current agent in the state
        state_manager.update_state(session_id, "current_agent", agent_type)

        return agent_type

    def get_agent(self, agent_type: str) -> Any:
        """
        Get the appropriate agent based on the agent type.

        Args:
            agent_type: The type of agent to get

        Returns:
            An agent instance
        """
        return self.agents.get(agent_type, root_agent)

    def enrich_user_message(self, user_message: str, session_id: str, agent_type: str) -> str:
        """
        Enrich the user message with context information.

        Args:
            user_message: The original user message
            session_id: Session identifier
            agent_type: The type of agent that will handle the message

        Returns:
            Enhanced user message with additional context
        """
        # Get conversation history context
        context_summary = state_manager.get_context_summary(session_id)

        # Get enhanced instructions for the specific agent type
        agent_specific_instructions = get_instructions_for_agent(agent_type)

        # Add itinerary information if available
        itinerary = state_manager.get_itinerary(session_id)
        itinerary_summary = ""
        if itinerary and itinerary.get("origin") and itinerary.get("destination"):
            itinerary_summary = (
                f"[ITINERARY INFORMATION]\n"
                f"Trip from {itinerary.get('origin')} to {itinerary.get('destination')}\n"
                f"Dates: {itinerary.get('start_date')} to {itinerary.get('end_date')}\n"
            )

            # Add days information if available
            if itinerary.get("days"):
                itinerary_summary += f"Total days: {len(itinerary.get('days'))}\n"

        # Create different context information based on agent type
        agent_specific_context = ""
        if agent_type == "restaurant":
            agent_specific_context = "This is a food and restaurant related query. You are the restaurant recommendation agent specializing in food experiences."
        elif agent_type == "activity":
            agent_specific_context = "This is an activity and attraction related query. You are the activity search agent specializing in attractions and things to do."
        else:
            agent_specific_context = "This is a general travel planning query. You are the main travel planning agent handling overall travel planning."

        # If we have context, prepend it to the user message
        enhanced_message = (
            f"[AGENT INSTRUCTIONS]\n"
            f"{agent_specific_instructions}\n\n"
            f"[AGENT CONTEXT]\n"
            f"{agent_specific_context}\n\n"
        )

        if itinerary_summary:
            enhanced_message += f"{itinerary_summary}\n\n"

        if context_summary:
            enhanced_message += (
                f"[CONVERSATION CONTEXT]\n"
                f"{context_summary}\n\n"
            )

        enhanced_message += (
            f"[CURRENT USER MESSAGE]\n"
            f"{user_message}\n\n"
            f"Please respond to the current user message with the conversation context in mind."
        )

        return enhanced_message

    async def process_message(self, 
                             user_message: str, 
                             session_id: str, 
                             runner: Runner) -> AsyncGenerator[Any, None]:
        """
        Process a user message with the appropriate agent.

        Args:
            user_message: The user's message
            session_id: Session identifier
            runner: The runner instance to use

        Returns:
            Generator yielding response events
        """
        # Store the user message in conversation history
        state_manager.add_user_message(session_id, user_message)

        # Classify the message intent
        agent_type = self.classify_intent(user_message, session_id)

        # Enrich the user message with context
        enhanced_message = self.enrich_user_message(user_message, session_id, agent_type)

        # Create content object for the agent
        content = Content(role="user", parts=[Part(text=enhanced_message)])

        # Variable to track final response
        final_response = None

        # Run the agent and capture the response
        async for event in runner.run_async(user_id="user_123", session_id=session_id, new_message=content):
            # Check if this is a final response
            if hasattr(event, 'is_final_response') and event.is_final_response():
                if event.content and hasattr(event.content, 'parts') and len(event.content.parts) > 0:
                    final_response = event.content.parts[0].text

            # Yield the event for processing
            yield event

        # Store the final response in conversation history
        if final_response:
            state_manager.add_agent_message(session_id, final_response, agent_type)

    def get_agent_with_context(self, agent_type: str, session_id: str) -> Tuple[Any, str]:
        """
        Get the appropriate agent along with context information.

        Args:
            agent_type: The type of agent to get
            session_id: Session identifier

        Returns:
            Tuple containing the agent instance and context string
        """
        agent = self.get_agent(agent_type)
        context = state_manager.get_context_summary(session_id)
        return agent, context

# Create a global orchestrator instance
improved_orchestrator = ImprovedAgentOrchestrator()
