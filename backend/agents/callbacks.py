"""
Custom implementation of callback classes for Google ADK.
This is needed because the current version of Google ADK doesn't have the callbacks module.
"""
from typing import Any, Dict


class AgentCallback:
    """Base class for agent callbacks."""
    
    def on_agent_start(self, agent, query):
        """Called when an agent starts processing a query."""
        pass
    
    def on_agent_end(self, agent, result):
        """Called when an agent completes processing a query."""
        pass
    
    def on_agent_error(self, agent, error):
        """Called when an agent encounters an error."""
        pass


class StreamingCallback(AgentCallback):
    """Callback for streaming agent responses."""
    
    def on_agent_start(self, agent, query):
        """Called when an agent starts processing a query."""
        print(f"[StreamingCallback] {agent.name} started processing query: {query}")
    
    def on_agent_end(self, agent, result):
        """Called when an agent completes processing a query."""
        print(f"[StreamingCallback] {agent.name} completed processing")
    
    def on_agent_error(self, agent, error):
        """Called when an agent encounters an error."""
        print(f"[StreamingCallback] {agent.name} encountered error: {error}")
