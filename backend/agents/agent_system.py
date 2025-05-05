import os
from typing import Dict, Any, List
from google.adk import SequentialAgent, ParallelAgent, Team
from google.adk.callbacks import AgentCallback, StreamingCallback
from google.adk.memory import ShortTermMemory, LongTermMemory
from google.adk.sessions import SessionManager

from .activity_agent import ActivitySearchAgent
from .restaurant_agent import RestaurantAgent
from .flight_agent import FlightSearchAgent
from .accommodation_agent import AccommodationAgent
from .video_agent import YouTubeVideoAgent
from .coordinator import TravelCoordinator

class TravelAgentSystem:
    def __init__(self):
        # Initialize memory systems
        self.short_term_memory = ShortTermMemory(capacity=100)
        self.long_term_memory = LongTermMemory(
            storage_backend="sqlite",
            db_path="travel_memory.db"
        )
        
        # Initialize session manager
        self.session_manager = SessionManager()
        
        # Initialize specialized agents
        self.activity_agent = ActivitySearchAgent()
        self.restaurant_agent = RestaurantAgent()
        self.flight_agent = FlightSearchAgent()
        self.accommodation_agent = AccommodationAgent()
        self.video_agent = YouTubeVideoAgent()
        
        # Initialize coordinator
        self.coordinator = TravelCoordinator()
        
        # Create agent team with parallel execution
        self.research_team = ParallelAgent(
            name="Research Team",
            agents=[
                self.activity_agent,
                self.restaurant_agent,
                self.flight_agent,
                self.accommodation_agent,
                self.video_agent
            ],
            aggregation_strategy=self._aggregate_results
        )
        
        # Create sequential workflow
        self.travel_planner = SequentialAgent(
            name="Travel Planner",
            agents=[
                self.coordinator,  # First understand requirements
                self.research_team,  # Then research in parallel
                self.coordinator   # Finally synthesize results
            ],
            pass_outputs=True
        )
        
        # Add callbacks
        self.travel_planner.add_callback(StreamingCallback())
        self.travel_planner.add_callback(LoggingCallback())
    
    async def plan_trip(self, departure: str, destination: str, 
                       start_date: str, end_date: str, 
                       budget: str, preferences: Dict = None) -> Dict:
        """
        Plan a complete trip using agent coordination
        """
        # Create or get session
        session = self.session_manager.create_session(
            user_id=f"{departure}_{destination}_{start_date}",
            metadata={
                "departure": departure,
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "budget": budget,
                "preferences": preferences or {}
            }
        )
        
        try:
            # Run the planning workflow
            result = await self.travel_planner.run_async({
                "departure": departure,
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "budget": budget,
                "preferences": preferences or {}
            })
            
            # Save to long-term memory
            self.long_term_memory.save(
                f"trip_{destination}_{start_date}",
                result
            )
            
            return result
        except Exception as e:
            print(f"Error in plan_trip: {e}")
            raise
    
    async def chat(self, message: str, session_id: str = None) -> Dict:
        """
        Chat with the travel agent for questions and refinements
        """
        session = None
        if session_id:
            session = self.session_manager.load_session(session_id)
        
        response = await self.coordinator.chat(message, session)
        
        return {
            "response": response,
            "session_id": session_id or "new_session"
        }
    
    async def get_destination_info(self, destination: str) -> Dict:
        """
        Get detailed information about a destination
        """
        # Check memory first
        cached_info = self.long_term_memory.load(f"destination_{destination}")
        if cached_info:
            return cached_info
        
        # Research destination
        info = await self.coordinator.research_destination(destination)
        
        # Cache result
        self.long_term_memory.save(f"destination_{destination}", info)
        
        return info
    
    def _aggregate_results(self, results: Dict[str, Any]) -> Dict:
        """
        Aggregate results from parallel agent execution
        """
        aggregated = {
            "activities": results.get("ActivitySearchAgent", {}).get("activities", []),
            "restaurants": results.get("RestaurantAgent", {}).get("restaurants", []),
            "flights": results.get("FlightSearchAgent", {}).get("flights", []),
            "accommodations": results.get("AccommodationAgent", {}).get("accommodations", []),
            "videos": results.get("YouTubeVideoAgent", {}).get("videos", [])
        }
        
        return aggregated
    
    def get_agent_statuses(self) -> Dict[str, str]:
        """
        Get status of all agents
        """
        return {
            "coordinator": "active",
            "activity_agent": "active",
            "restaurant_agent": "active",
            "flight_agent": "active",
            "accommodation_agent": "active",
            "video_agent": "active"
        }

class LoggingCallback(AgentCallback):
    def on_agent_start(self, agent, query):
        print(f"[{agent.name}] Starting with query: {query}")
    
    def on_agent_end(self, agent, result):
        print(f"[{agent.name}] Completed with result")
    
    def on_agent_error(self, agent, error):
        print(f"[{agent.name}] Error: {error}")
