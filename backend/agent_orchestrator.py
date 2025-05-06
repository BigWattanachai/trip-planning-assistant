"""
Agent Orchestrator: A module that coordinates between multiple agents
"""
from typing import Dict, List, Any, Optional, Tuple
from google.adk.runners import Runner
from google.genai.types import Part, Content
from conversation_history import conversation_history
from agents.travel_agent import classify_intent, root_agent
from agents.activity_search_agent import activity_search_agent
from agents.restaurant_agent import restaurant_agent
from agent_instructions import get_instructions_for_agent

class AgentOrchestrator:
    """
    Orchestrates requests between multiple specialized agents.
    
    This class manages the flow of information between different agents,
    ensuring that user queries are sent to the appropriate agent while
    maintaining conversation context.
    """
    
    def __init__(self):
        """Initialize the agent orchestrator"""
        # Map of agent types to agent instances
        self.agents = {
            "travel": root_agent,
            "activity": activity_search_agent,
            "restaurant": restaurant_agent
        }
        
        # Map of recent agent types used per session
        self.session_agents: Dict[str, str] = {}
    
    def classify_intent(self, user_message: str, session_id: str) -> str:
        """
        Determine which agent should handle the user message.
        
        Args:
            user_message: The user's message
            session_id: Session identifier
            
        Returns:
            String identifying the agent type that should handle the request
        """
        # Use the intent classifier with session context
        agent_type = classify_intent(user_message, session_id)
        
        # Store the most recent agent type for this session
        self.session_agents[session_id] = agent_type
        
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
        context_summary = conversation_history.get_context_summary(session_id)
        
        # Get enhanced instructions for the specific agent type
        agent_specific_instructions = get_instructions_for_agent(agent_type)
        
        # Create different context information based on agent type
        agent_specific_context = ""
        if agent_type == "restaurant":
            agent_specific_context = "This is a food and restaurant related query. You are the restaurant recommendation agent specializing in food experiences."
        elif agent_type == "activity":
            agent_specific_context = "This is an activity and attraction related query. You are the activity search agent specializing in attractions and things to do."
        else:
            agent_specific_context = "This is a general travel planning query. You are the main travel planning agent handling overall travel planning."
        
        # If we have context, prepend it to the user message
        if context_summary:
            enhanced_message = (
                f"[AGENT INSTRUCTIONS]\n"
                f"{agent_specific_instructions}\n\n"
                f"[AGENT CONTEXT]\n"
                f"{agent_specific_context}\n\n"
                f"[CONVERSATION CONTEXT]\n"
                f"{context_summary}\n\n"
                f"[CURRENT USER MESSAGE]\n"
                f"{user_message}\n\n"
                f"Please respond to the current user message with the conversation context in mind."
            )
            return enhanced_message
        
        # Otherwise, just add minimal context
        return (
            f"[AGENT INSTRUCTIONS]\n"
            f"{agent_specific_instructions}\n\n"
            f"[AGENT CONTEXT]\n"
            f"{agent_specific_context}\n\n"
            f"[CURRENT USER MESSAGE]\n"
            f"{user_message}"
        )
    
    async def process_message(self, user_message: str, session_id: str, runner: Runner) -> Dict[str, Any]:
        """
        Process a user message with the appropriate agent.
        
        Args:
            user_message: The user's message
            session_id: Session identifier
            runner: The runner instance to use
            
        Returns:
            Generator yielding response parts
        """
        # Store the user message in conversation history
        conversation_history.add_user_message(session_id, user_message)
        
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
            conversation_history.add_agent_message(session_id, final_response, agent_type)

# Create a global orchestrator instance
orchestrator = AgentOrchestrator()
