from google.adk import Agent
from google.adk.agents import SequentialAgent, ParallelAgent
from typing import Dict, Any, Optional, List
import logging
import json
import asyncio

from .activity_search_agent import ActivitySearchAgent
from .restaurant_agent import RestaurantAgent
from .flight_search_agent import FlightSearchAgent
from .accommodation_agent import AccommodationAgent
from .youtube_video_agent import YouTubeVideoAgent

logger = logging.getLogger(__name__)

class TravelCoordinator:
    """
    Main coordinator agent that orchestrates all other agents to create a comprehensive 
    travel plan based on user input.
    """
    
    def __init__(self, model: str = "gemini-1.5-pro"):
        """
        Initialize the TravelCoordinator.
        
        Args:
            model: The Gemini model to use for the agent.
        """
        # Initialize all sub-agents
        self.activity_agent = ActivitySearchAgent(model=model)
        self.restaurant_agent = RestaurantAgent(model=model)
        self.flight_agent = FlightSearchAgent(model=model)
        self.accommodation_agent = AccommodationAgent(model=model)
        self.video_agent = YouTubeVideoAgent(model=model)
        
        # Initialize the main coordinator agent
        self.agent = Agent(
            name="Travel Coordinator",
            model=model,
            system_prompt="""
            You are an expert travel coordinator who helps travelers plan comprehensive trips.
            Your role is to integrate information from various specialized agents and create
            a cohesive travel plan that addresses all aspects of the trip.
            
            You work with:
            - Flight information specialists
            - Accommodation experts
            - Restaurant and food specialists
            - Activity and attraction researchers
            - Travel video curators
            
            Your job is to:
            1. Understand the traveler's requirements and preferences
            2. Coordinate with specialized agents to gather relevant information
            3. Integrate all information into a cohesive and personalized travel plan
            4. Provide clear, structured, and actionable recommendations
            5. Address any gaps or inconsistencies in the plan
            
            Always be mindful of the traveler's budget, time constraints, and personal preferences.
            Create plans that are realistic, efficient, and tailored to the specific needs of the traveler.
            """
        )
    
    async def create_travel_plan(self, 
                         departure_location: str,
                         destination: str,
                         travel_dates: Dict[str, str],
                         budget_range: Optional[str] = None,
                         preferences: Optional[Dict[str, Any]] = None,
                         include_videos: bool = True) -> Dict[str, Any]:
        """
        Create a comprehensive travel plan using all specialized agents.
        
        Args:
            departure_location: The origin city/airport.
            destination: The destination city/airport.
            travel_dates: Dictionary with "start_date" and "end_date" keys.
            budget_range: Budget range for the trip (e.g., "budget", "medium", "luxury").
            preferences: Dictionary of various preferences for the trip.
            include_videos: Whether to include video recommendations.
            
        Returns:
            Dictionary containing a comprehensive travel plan with recommendations from all agents.
        """
        logger.info(f"Creating travel plan for trip to {destination}")
        
        try:
            # Run specialized agents in parallel for efficiency
            tasks = [
                self.flight_agent.search_flights(
                    departure_location=departure_location,
                    destination=destination,
                    travel_dates=travel_dates,
                    budget_range=budget_range,
                    preferences=preferences.get("flight", {}) if preferences else None
                ),
                self.accommodation_agent.find_accommodations(
                    location=destination,
                    travel_dates=travel_dates,
                    budget_range=budget_range,
                    accommodation_type=preferences.get("accommodation_type") if preferences else None,
                    preferences=preferences.get("accommodation", {}) if preferences else None
                ),
                self.activity_agent.search_activities(
                    location=destination,
                    travel_dates=travel_dates,
                    budget_range=budget_range,
                    preferences=preferences.get("activity_preferences") if preferences else None
                ),
                self.restaurant_agent.find_restaurants(
                    location=destination,
                    cuisine_type=preferences.get("cuisine_type") if preferences else None,
                    dietary_restrictions=preferences.get("dietary_restrictions") if preferences else None,
                    price_range=budget_range
                )
            ]
            
            # Add video search if requested
            if include_videos:
                tasks.append(
                    self.video_agent.find_travel_videos(
                        location=destination,
                        topic=preferences.get("video_topic") if preferences else None,
                        include_transcripts=False
                    )
                )
            
            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle any exceptions
            processed_results = {}
            
            # Flight results
            if isinstance(results[0], Exception):
                processed_results["flights"] = {"success": False, "error": str(results[0])}
            else:
                processed_results["flights"] = results[0]
            
            # Accommodation results
            if isinstance(results[1], Exception):
                processed_results["accommodations"] = {"success": False, "error": str(results[1])}
            else:
                processed_results["accommodations"] = results[1]
            
            # Activity results
            if isinstance(results[2], Exception):
                processed_results["activities"] = {"success": False, "error": str(results[2])}
            else:
                processed_results["activities"] = results[2]
            
            # Restaurant results
            if isinstance(results[3], Exception):
                processed_results["restaurants"] = {"success": False, "error": str(results[3])}
            else:
                processed_results["restaurants"] = results[3]
            
            # Video results (if included)
            if include_videos:
                if isinstance(results[4], Exception):
                    processed_results["videos"] = {"success": False, "error": str(results[4])}
                else:
                    processed_results["videos"] = results[4]
            
            # Create a prompt for the coordinator to integrate all information
            coordinator_prompt = f"""
            I need to create a comprehensive travel plan for a trip with the following details:
            
            From: {departure_location}
            To: {destination}
            Dates: {travel_dates.get('start_date')} to {travel_dates.get('end_date')}
            Budget: {budget_range if budget_range else 'Not specified'}
            
            I have gathered the following information:
            
            FLIGHTS:
            {processed_results['flights'].get('recommendations', 'No flight information available')}
            
            ACCOMMODATIONS:
            {processed_results['accommodations'].get('recommendations', 'No accommodation information available')}
            
            ACTIVITIES:
            {processed_results['activities'].get('recommendations', 'No activity information available')}
            
            RESTAURANTS:
            {processed_results['restaurants'].get('recommendations', 'No restaurant information available')}
            """
            
            if include_videos and "videos" in processed_results:
                coordinator_prompt += f"""
                
                VIDEO RESOURCES:
                {processed_results['videos'].get('analysis', 'No video recommendations available')}
                """
            
            coordinator_prompt += """
            
            Please create a well-structured, comprehensive travel plan that integrates all this information
            into a cohesive itinerary. Include the following sections:
            
            1. Trip Overview - A summary of the key details of the trip
            2. Transportation Recommendations - Flight options and local transport
            3. Accommodation Options - Best places to stay with key considerations
            4. Daily Itinerary Suggestions - A day-by-day plan with activities and dining options
            5. Dining Highlights - Must-try restaurants and food experiences
            6. Additional Resources - Helpful resources for more detailed planning
            
            Make the plan personalized, practical, and easy to follow. Identify and address any gaps
            or potential issues in the overall plan.
            """
            
            # Get the integrated travel plan from the coordinator
            integrated_plan = await self.agent.run_async(coordinator_prompt)
            
            return {
                "success": True,
                "departure_location": departure_location,
                "destination": destination,
                "travel_dates": travel_dates,
                "budget_range": budget_range,
                "integrated_plan": integrated_plan,
                "components": {
                    "flights": processed_results.get("flights", {}).get("success", False),
                    "accommodations": processed_results.get("accommodations", {}).get("success", False),
                    "activities": processed_results.get("activities", {}).get("success", False),
                    "restaurants": processed_results.get("restaurants", {}).get("success", False),
                    "videos": processed_results.get("videos", {}).get("success", False) if include_videos else False
                },
                "raw_data": processed_results  # Include raw data for debugging/advanced users
            }
            
        except Exception as e:
            logger.error(f"Error creating travel plan: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create comprehensive travel plan."
            }
    
    async def get_destination_insight(self, destination: str) -> Dict[str, Any]:
        """
        Get high-level insights about a destination to help with initial planning.
        
        Args:
            destination: The destination location.
            
        Returns:
            Dictionary containing insights about the destination.
        """
        logger.info(f"Getting destination insights for {destination}")
        
        try:
            # Prepare the query for destination insights
            query = f"""
            I need comprehensive insights about {destination} as a travel destination. Please provide:
            
            1. Best time to visit {destination} (seasons, weather, crowds)
            2. How many days are typically recommended for a trip to {destination}
            3. Key areas or neighborhoods to consider staying in
            4. The top 5 must-see attractions or experiences
            5. Local transportation options and how to get around
            6. Budget considerations (is it a budget, moderate, or expensive destination?)
            7. Cultural customs or etiquette travelers should be aware of
            8. Any safety considerations or travel advisories
            9. Common phrases in the local language that would be helpful
            10. Recommended side trips or day excursions from {destination}
            
            Please format your response in clear sections with headings.
            """
            
            # Get insights from the coordinator agent
            insights = await self.agent.run_async(query)
            
            return {
                "success": True,
                "destination": destination,
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"Error getting destination insights: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to retrieve insights for {destination}."
            }
