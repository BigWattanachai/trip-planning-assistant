# Travel A2A Backend

This is the backend for the Travel A2A application, built using Google's Agent Development Kit (ADK). It consists of several specialized agents coordinated by a main TravelCoordinator agent.

## Project Structure

```
backend/
├── agents/                    # Agents directory
│   ├── __init__.py           # Package initialization
│   ├── activity_search_agent.py     # Activities and attractions agent
│   ├── restaurant_agent.py          # Restaurants and dining agent
│   ├── flight_search_agent.py       # Flight search agent
│   ├── accommodation_agent.py       # Accommodation search agent
│   ├── youtube_video_agent.py       # YouTube travel videos agent
│   └── travel_coordinator.py        # Main coordinator agent
├── .env                      # Environment variables (create from .env.example)
├── .env.example              # Example environment file
├── main.py                   # FastAPI application entry point
├── requirements.txt          # Project dependencies
└── README.md                 # This file
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- Virtual environment tool (e.g., venv, conda)
- Google AI API key

### Installation

1. Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows (CMD):
.venv\Scripts\activate.bat
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
# Copy the example .env file
cp .env.example .env

# Edit the .env file with your API keys
# Replace 'your_api_key_here' with your actual Google AI API key
```

### Running the Server

Start the FastAPI server:

```bash
python main.py
```

The server will start on http://localhost:8000 by default.

## API Endpoints

- **Health Check**: `GET /api/health`
- **WebSocket**: `WS /api/ws/{session_id}` - For real-time conversation with agents
- **Plan Trip**: `POST /api/plan_trip` - Plan a complete trip
- **Search Activities**: `GET /api/search_activities` - Find activities at a destination
- **Search Restaurants**: `GET /api/search_restaurants` - Find restaurants at a destination
- **Search Flights**: `GET /api/search_flights` - Find flights between locations
- **Search Accommodations**: `GET /api/search_accommodations` - Find places to stay
- **Search Travel Videos**: `GET /api/search_travel_videos` - Find travel-related YouTube videos

## Agent Descriptions

1. **ActivitySearchAgent**: Specializes in finding and recommending activities and attractions at travel destinations.
2. **RestaurantAgent**: Focuses on dining options and restaurant recommendations.
3. **FlightSearchAgent**: Handles flight search and booking recommendations.
4. **AccommodationAgent**: Specializes in finding and recommending places to stay.
5. **YouTubeVideoAgent**: Finds and recommends travel-related YouTube videos.
6. **TravelCoordinator**: Main agent that coordinates all other agents to provide comprehensive travel planning.

## Development Notes

- The current implementation uses Google Search for information retrieval. In a production environment, you would integrate with actual travel APIs.
- This backend is designed to work with the Travel A2A frontend.
- The WebSocket endpoint provides real-time streaming communication with the agent.
