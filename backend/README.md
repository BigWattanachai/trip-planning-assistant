# Travel A2A Backend

This is the backend application for the Travel A2A project, which provides AI-powered travel planning services.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Google API Key for Gemini (for the AI capabilities)

### Environment Setup

1. Create a virtual environment:

```bash
# Create the virtual environment
python -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate.bat (CMD)
# .venv\Scripts\Activate.ps1 (PowerShell)
```

2. Set up environment variables by copying `.env.example` to `.env`:

```bash
cp .env.example .env
```

3. Edit the `.env` file and add your Google API Key:

```
GOOGLE_API_KEY=your_api_key_here
```

### Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the server:

```bash
python main.py
```

The server will run on `http://localhost:8000` by default (configurable in the `.env` file).

## API Endpoints

The backend provides the following endpoints:

- WebSocket: `/api/ws/{session_id}` - For real-time chat with the travel planning assistant
- Health Check: `/api/health` - To check if the server is running
- Trip Planning: `/api/plan_trip` - To plan a complete trip
- Activities: `/api/search_activities` - To search for activities at a destination
- Restaurants: `/api/search_restaurants` - To search for restaurants at a destination
- Flights: `/api/search_flights` - To search for flights between locations
- Accommodations: `/api/search_accommodations` - To search for accommodations at a destination
- Travel Videos: `/api/search_travel_videos` - To search for travel-related videos about a destination

## Architecture

The backend uses:

- FastAPI for the web framework
- Google ADK (Agent Development Kit) for the AI capabilities
- WebSockets for real-time bidirectional communication
- In-memory session management for stateful conversations

## Agent Structure

The backend is organized around several AI agents:

- `travel_coordinator` - The main agent that coordinates all other agents
- `activity_search_agent` - Specializes in finding activities and attractions
- `restaurant_agent` - Specializes in finding restaurants and dining options
- `flight_search_agent` - Specializes in finding flights and transportation
- `accommodation_agent` - Specializes in finding accommodations
- `youtube_video_agent` - Specializes in finding travel-related videos

## WebSocket Communication

The WebSocket endpoint (`/api/ws/{session_id}`) enables real-time communication with the AI agent. The communication format is JSON with the following structure:

- From client to server: Plain text messages
- From server to client: JSON objects with the following structure:
  - `message`: The text response from the AI
  - `turn_complete`: Boolean indicating if the AI has completed its response
  - `interrupted`: Boolean indicating if the AI's response was interrupted

## Troubleshooting

- **API Key Issues**: Make sure your Google API Key is valid and has access to the Gemini API
- **Import Errors**: Make sure all dependencies are installed correctly
- **Connection Issues**: Check if the server is running and the ports are not blocked by a firewall

## Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add some amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request
