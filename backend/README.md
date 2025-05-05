# Travel A2A Backend API

Backend API for the Travel Planning Application using Google Agent-to-Agent (A2A) architecture with MCP integration.

## Features

- Multi-agent system for comprehensive travel planning
- Specialized agents for different aspects of travel:
  - Activities and attractions
  - Restaurant recommendations
  - Flight search
  - Accommodation search
  - YouTube travel videos
- Agent coordination and orchestration
- Session management and memory systems
- MCP integration for external services
- RESTful API endpoints

## Tech Stack

- FastAPI
- Google ADK (Agent Development Kit)
- Google Cloud AI Platform
- Gemini Models
- MCP (Model Context Protocol)

## Prerequisites

- Python 3.9+
- Google Cloud Project with Gemini API access
- API keys for external services

## Installation

1. Clone the repository and navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your API keys and configuration.

## Configuration

Required environment variables:

```env
# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_LOCATION=us-central1

# API Keys
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_SEARCH_API_KEY=your-google-search-api-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id
YOUTUBE_API_KEY=your-youtube-api-key

# External Service API Keys (optional)
SKYSCANNER_API_KEY=your-skyscanner-api-key
TRIPADVISOR_API_KEY=your-tripadvisor-api-key
OPENWEATHER_API_KEY=your-openweather-api-key

# Server Configuration
PORT=8000
HOST=0.0.0.0
ENV=development

# MCP Configuration
MCP_SERVER_URL=http://mcp-server:8080
MCP_API_KEY=your-mcp-api-key
```

## Running the Server

Development mode:
```bash
python main.py
```

Production mode:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### POST /api/plan-trip
Plan a complete trip based on user requirements.

Request body:
```json
{
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
```

### POST /api/chat
Chat with the travel agent for questions and refinements.

Request body:
```json
{
  "message": "What are the best areas to stay in Bangkok?",
  "sessionId": "optional-session-id"
}
```

### GET /api/health
Health check endpoint.

### GET /api/destinations/{destination}
Get detailed information about a destination.

## Agent Architecture

The system uses a multi-agent architecture with:

1. **Travel Coordinator**: Main orchestrator agent
2. **Activity Search Agent**: Finds attractions and activities
3. **Restaurant Agent**: Recommends dining options
4. **Flight Search Agent**: Searches for flights
5. **Accommodation Agent**: Finds hotels and rentals
6. **YouTube Video Agent**: Curates relevant travel videos

Agents work in parallel for efficiency and use the coordinator for synthesis.

## MCP Integration

The backend integrates with MCP (Model Context Protocol) for:
- External API calls
- Real-time data fetching
- Service orchestration

MCP provides a standardized way to interact with external services while maintaining security and reliability.

## Development

To add a new agent:

1. Create a new agent class extending `LlmAgent` or `BaseAgent`
2. Implement the `run_async` method
3. Add custom tools if needed
4. Register the agent in `agent_system.py`

Example:
```python
from google.adk import LlmAgent

class NewAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="New Agent",
            model="gemini-1.5-flash",
            system_prompt="Your agent's purpose..."
        )
    
    async def run_async(self, context: Dict) -> Dict:
        # Agent logic here
        return results
```

## Testing

Run tests:
```bash
pytest tests/
```

## Deployment

1. Build Docker image:
```bash
docker build -t travel-a2a-backend .
```

2. Run container:
```bash
docker run -p 8000:8000 --env-file .env travel-a2a-backend
```

## License

MIT License
