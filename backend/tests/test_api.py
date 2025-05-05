import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

# Sample test data
test_trip_request = {
    "departure": "San Francisco",
    "destination": "Bangkok",
    "startDate": "2024-06-01",
    "endDate": "2024-06-10",
    "budgetRange": "medium",
    "preferences": {
        "activities": ["cultural", "food", "shopping"],
        "accommodation_type": "hotel",
        "dietary": ["vegetarian"]
    }
}

test_chat_message = {
    "message": "What are the best areas to stay in Bangkok?",
    "sessionId": "test_session_123"
}

# Sample response data
mock_trip_response = {
    "destination": "Bangkok",
    "departure": "San Francisco",
    "startDate": "2024-06-01",
    "endDate": "2024-06-10",
    "budget": "medium",
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
    ],
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
    ],
    "flights": [],
    "accommodations": [],
    "videos": [],
    "summary": "Test trip summary"
}

mock_chat_response = {
    "response": "I recommend staying in the Sukhumvit area for good access to public transportation and modern amenities.",
    "session_id": "test_session_123"
}

# Tests
@pytest.mark.asyncio
@patch('agents.agent_system.TravelAgentSystem.plan_trip')
async def test_plan_trip(mock_plan_trip):
    # Setup mock
    mock_plan_trip.return_value = mock_trip_response
    
    # Call endpoint
    response = client.post("/api/plan-trip", json=test_trip_request)
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["destination"] == "Bangkok"
    assert data["departure"] == "San Francisco"
    assert len(data["activities"]) == 1
    assert data["activities"][0]["name"] == "Grand Palace"
    
    # Verify mock was called with correct args
    mock_plan_trip.assert_called_once()
    call_args = mock_plan_trip.call_args[1]
    assert call_args["departure"] == "San Francisco"
    assert call_args["destination"] == "Bangkok"
    assert call_args["budget"] == "medium"

@pytest.mark.asyncio
@patch('agents.agent_system.TravelAgentSystem.chat')
async def test_chat_with_agent(mock_chat):
    # Setup mock
    mock_chat.return_value = mock_chat_response
    
    # Call endpoint
    response = client.post("/api/chat", json=test_chat_message)
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "Sukhumvit" in data["response"]
    assert data["sessionId"] == "test_session_123"
    
    # Verify mock was called with correct args
    mock_chat.assert_called_once_with(
        message="What are the best areas to stay in Bangkok?",
        session_id="test_session_123"
    )

@pytest.mark.asyncio
@patch('agents.agent_system.TravelAgentSystem.get_destination_info')
async def test_get_destination_info(mock_get_info):
    # Setup mock
    mock_get_info.return_value = {
        "overview": "Bangkok is the capital of Thailand",
        "highlights": ["Grand Palace", "Wat Pho", "Chatuchak Market"],
        "best_time_to_visit": "November to February"
    }
    
    # Call endpoint
    response = client.get("/api/destinations/Bangkok")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["destination"] == "Bangkok"
    assert "capital of Thailand" in data["overview"]
    assert len(data["highlights"]) == 3
    assert data["highlights"][0] == "Grand Palace"

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "agents" in data
    assert "version" in data

@pytest.mark.asyncio
@patch('services.mcp_integration.MCPIntegration.get_weather_forecast')
async def test_get_weather(mock_weather):
    # Setup mock
    mock_weather.return_value = {
        "current": {
            "temperature": 32,
            "description": "Sunny"
        },
        "forecast": [
            {
                "date": "2024-06-01",
                "temperature": 31,
                "description": "Partly cloudy"
            }
        ]
    }
    
    # Call endpoint
    response = client.get("/api/weather/Bangkok")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["destination"] == "Bangkok"
    assert data["currentConditions"] == "Sunny"
    assert data["temperature"] == 32
    assert len(data["forecast"]) == 1
