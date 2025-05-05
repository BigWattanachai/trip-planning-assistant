import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
import json
from datetime import datetime

# Add parent directory to path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.activity_agent import ActivitySearchAgent
from agents.restaurant_agent import RestaurantAgent
from agents.flight_agent import FlightSearchAgent
from agents.accommodation_agent import AccommodationAgent
from agents.video_agent import YouTubeVideoAgent
from agents.coordinator import TravelCoordinator
from agents.agent_system import TravelAgentSystem

# Common test context
test_context = {
    "departure": "San Francisco",
    "destination": "Bangkok",
    "start_date": "2024-06-01",
    "end_date": "2024-06-10",
    "budget": "medium",
    "preferences": {
        "activities": ["cultural", "food", "shopping"],
        "accommodation_type": "hotel",
        "dietary": ["vegetarian"]
    }
}

@pytest.fixture
def mock_search_tool():
    """Create a mock search tool"""
    with patch('google.adk.tools.search_tool') as mock:
        mock.return_value = AsyncMock()
        yield mock

@pytest.fixture
def mock_function_tool():
    """Create a mock function tool"""
    with patch('google.adk.tools.function_tool') as mock:
        mock.return_value = AsyncMock()
        yield mock

@pytest.mark.asyncio
async def test_activity_agent(mock_search_tool, mock_function_tool):
    """Test the ActivitySearchAgent"""
    # Create mock agent with mocked tools
    agent = ActivitySearchAgent()
    
    # Mock the use_tool method
    agent.use_tool = AsyncMock()
    agent.use_tool.return_value = {
        "activities": [
            {
                "id": "1",
                "name": "Grand Palace",
                "description": "Historic royal palace complex",
                "rating": 4.7,
                "openingHours": "8:30 AM - 3:30 PM",
                "imageUrl": "https://example.com/grand-palace.jpg",
                "category": "Cultural"
            }
        ]
    }
    
    # Mock generate_async method
    agent.generate_async = AsyncMock()
    agent.generate_async.return_value = "Activity recommendations for Bangkok..."
    
    # Call run_async
    result = await agent.run_async(test_context)
    
    # Assertions
    assert isinstance(result, dict)
    assert "activities" in result
    assert len(result["activities"]) == 1
    assert result["activities"][0]["name"] == "Grand Palace"
    assert "recommendations" in result
    
    # Verify tool calls
    assert agent.use_tool.call_count >= 1

@pytest.mark.asyncio
async def test_restaurant_agent(mock_search_tool, mock_function_tool):
    """Test the RestaurantAgent"""
    # Create mock agent with mocked tools
    agent = RestaurantAgent()
    
    # Mock the use_tool method
    agent.use_tool = AsyncMock()
    agent.use_tool.return_value = {
        "restaurants": [
            {
                "id": "1",
                "name": "Thai Delight",
                "cuisine": "Thai",
                "priceRange": "$$",
                "rating": 4.6,
                "reviewHighlight": "Authentic Thai flavors",
                "imageUrl": "https://example.com/thai-delight.jpg"
            }
        ]
    }
    
    # Mock generate_async method
    agent.generate_async = AsyncMock()
    agent.generate_async.return_value = "Restaurant recommendations for Bangkok..."
    
    # Call run_async
    result = await agent.run_async(test_context)
    
    # Assertions
    assert isinstance(result, dict)
    assert "restaurants" in result
    assert len(result["restaurants"]) == 1
    assert result["restaurants"][0]["name"] == "Thai Delight"
    assert "recommendations" in result
    
    # Verify tool calls
    assert agent.use_tool.call_count >= 1

@pytest.mark.asyncio
async def test_coordinator_agent(mock_search_tool):
    """Test the TravelCoordinator"""
    # Create mock agent with mocked tools
    agent = TravelCoordinator()
    
    # Mock generate_async method
    agent.generate_async = AsyncMock()
    agent.generate_async.return_value = "Trip planning analysis for Bangkok..."
    
    # Mock the use_tool method
    agent.use_tool = AsyncMock()
    agent.use_tool.return_value = "Search results for Bangkok travel..."
    
    # Call run_async with initial context
    result = await agent.run_async(test_context)
    
    # Assertions for initial planning
    assert isinstance(result, dict)
    assert "analysis" in result
    assert result["destination"] == "Bangkok"
    assert result["budget"] == "medium"
    
    # Test with results from other agents
    context_with_results = {
        **test_context,
        "activities": [{"id": "1", "name": "Grand Palace"}],
        "restaurants": [{"id": "1", "name": "Thai Delight"}],
        "flights": [{"id": "1", "airline": "Thai Airways"}],
        "accommodations": [{"id": "1", "name": "Bangkok Hotel"}],
        "videos": [{"id": "1", "title": "Bangkok Travel Guide"}]
    }
    
    # Call run_async with results
    result = await agent.run_async(context_with_results)
    
    # Assertions for results synthesis
    assert isinstance(result, dict)
    assert "summary" in result
    assert result["destination"] == "Bangkok"
    assert "activities" in result
    assert "restaurants" in result
    assert "flights" in result
    assert "accommodations" in result
    assert "videos" in result

@pytest.mark.asyncio
async def test_agent_system():
    """Test the TravelAgentSystem"""
    # Create mock system
    system = TravelAgentSystem()
    
    # Mock travel_planner.run_async
    system.travel_planner.run_async = AsyncMock()
    system.travel_planner.run_async.return_value = {
        "destination": "Bangkok",
        "departure": "San Francisco",
        "startDate": "2024-06-01",
        "endDate": "2024-06-10",
        "budget": "medium",
        "activities": [{"id": "1", "name": "Grand Palace"}],
        "restaurants": [{"id": "1", "name": "Thai Delight"}],
        "flights": [{"id": "1", "airline": "Thai Airways"}],
        "accommodations": [{"id": "1", "name": "Bangkok Hotel"}],
        "videos": [{"id": "1", "title": "Bangkok Travel Guide"}],
        "summary": "Trip plan summary for Bangkok..."
    }
    
    # Call plan_trip
    result = await system.plan_trip(
        departure="San Francisco",
        destination="Bangkok",
        start_date="2024-06-01",
        end_date="2024-06-10",
        budget="medium"
    )
    
    # Assertions
    assert isinstance(result, dict)
    assert result["destination"] == "Bangkok"
    assert "activities" in result
    assert "restaurants" in result
    assert "flights" in result
    assert "accommodations" in result
    assert "videos" in result
    assert "summary" in result
    
    # Test chat method
    system.coordinator.chat = AsyncMock()
    system.coordinator.chat.return_value = "Chat response about Bangkok travel..."
    
    chat_result = await system.chat(
        message="What are the best areas to stay in Bangkok?",
        session_id="test_session_123"
    )
    
    assert isinstance(chat_result, dict)
    assert "response" in chat_result
    assert "session_id" in chat_result
