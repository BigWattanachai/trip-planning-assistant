# Travel A2A Backend

This is the backend application for the Travel A2A project, which provides AI-powered travel planning services using Google's Agent Development Kit (ADK).

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

## Architecture

The backend is built using FastAPI and Google ADK, with a multi-agent architecture:

1. **Root Agent (Travel Agent)**: A SequentialAgent that orchestrates specialized agents
2. **Activity Search Agent**: Helps find activities and attractions in a destination
3. **Restaurant Agent**: Helps find restaurants and food experiences in a destination
4. **Summary Agent**: Synthesizes responses from specialized agents

## Agent Capabilities

### Travel Agent
- Orchestrates the specialized agents in sequence
- Provides a coherent response to the user by combining information from specialized agents

### Activity Search Agent
- Searches for activities in a destination
- Provides detailed information about specific attractions
- Uses tools:
  - `search_activities`: Finds activities based on location and interests
  - `get_activity_details`: Gets detailed information about a specific activity

### Restaurant Agent
- Searches for restaurants in a destination
- Provides detailed information about specific restaurants
- Uses tools:
  - `search_restaurants`: Finds restaurants based on location, cuisine type, and dietary requirements
  - `get_restaurant_details`: Gets detailed information about a specific restaurant

## API Endpoints

The backend provides the following endpoints:

- `/api/ws/{session_id}`: WebSocket endpoint for real-time communication with the default travel agent
- `/api/ws/{session_id}/{agent_type}`: WebSocket endpoint for real-time communication with a specific agent
- `/api/health`: Health check endpoint
- `/api/agents`: List available agents

## WebSocket Communication

The WebSocket endpoints enable real-time communication with the AI agents. The communication format is JSON with the following structure:

- From client to server: Plain text messages
- From server to client: JSON objects with the following structure:
  - `message`: The text response from the AI
  - `turn_complete`: Boolean indicating if the AI has completed its response

## Development

The backend uses Google ADK's event-based architecture to handle agent responses, including function calls and responses. The `get_agent_response` function in `main.py` processes these events and returns the final response to the client.

To add new agents or tools, follow these steps:

1. Create a new agent file in the `agents` directory
2. Define any tools as Python functions with proper docstrings
3. Create an Agent instance with the tools
4. Import the agent in `main.py` and add it to the agent selection logic

## Troubleshooting

- **API Key Issues**: Make sure your Google API Key is valid and has access to the Gemini API
- **Import Errors**: Make sure all dependencies are installed correctly
- **Connection Issues**: Check if the server is running and the ports are not blocked by a firewall

## Deployment

The backend can be deployed using Docker:

```bash
docker build -t travel-a2a-backend .
docker run -p 8000:8000 travel-a2a-backend
```

## Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add some amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request
