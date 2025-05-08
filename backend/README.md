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
# Method 1: Run as a module (recommended)
# From the travel-a2a directory (not from inside the backend directory)
python -m backend.main

# Method 2: Run directly
# From the travel-a2a/backend directory
python main.py
```

The server will run on `http://localhost:8000` by default (configurable in the `.env` file).

## Project Structure

The backend is organized into the following directories:

- `/agents/` - Agent implementations for different specialized domains
- `/api/` - API endpoints and WebSocket handlers
- `/core/` - Core functionality like state management and orchestration
- `/services/` - Services like itinerary management
- `/utils/` - Utility functions and helpers

## Architecture Overview

The system uses a multi-agent approach with the following components:

1. **State Manager**: Central repository for maintaining conversation state and user context
2. **Agent Orchestrator**: Coordinates between specialized agents, handling context-aware routing
3. **Itinerary Manager**: Manages travel itinerary creation and modification
4. **Specialized Agents**: Domain-specific agents for different aspects of travel planning

### Agent Capabilities

#### Travel Agent (Root Agent)
- Orchestrates the specialized agents
- Provides general travel planning advice
- Answers questions about destinations in Thailand
- Suggests itineraries and travel routes
- Advises on travel logistics (transportation, accommodations, timing)
- Provides budget information and general costs
- Handles queries that don't clearly fit into food or activity categories

#### Activity Search Agent
- Specializes in finding activities and attractions
- Provides detailed information about things to do
- Aware of user interests and previous preferences
- Uses tools:
  - `search_activities`: Finds activities based on location and interests
  - `get_activity_details`: Gets detailed information about a specific activity

#### Restaurant Agent
- Specializes in food and dining recommendations
- Considers dietary preferences and restrictions
- Can suggest culinary experiences based on location
- Uses tools:
  - `search_restaurants`: Finds restaurants based on location, cuisine type, and dietary requirements
  - `get_restaurant_details`: Gets detailed information about a specific restaurant

### Intent Classification

The system classifies user requests into three categories:
- **Restaurant Intent**: Queries about food, restaurants, dining, etc.
- **Activity Intent**: Queries about attractions, places to visit, things to do, etc.
- **General Travel Intent**: General queries or ambiguous requests

The intent classification algorithm uses a weighted keyword matching approach:
1. Check for high-priority patterns (e.g., "ร้าน" + "อร่อย" for restaurant intent)
2. Count weighted occurrences of keywords from predefined lists
3. Apply special phrase boosts for particular expressions
4. Compare scores with thresholds to determine intent

### State Management

The state management approach is inspired by ADK's state model, with specialized tools for:

- **Memorization**: Storing key-value pairs in the session state
- **Entity Recognition**: Extracting locations, activities, and preferences
- **Context Summarization**: Creating concise summaries of relevant context
- **Follow-up Detection**: Identifying follow-up questions to maintain context

### Agent Flow

1. **User Message Received**: WebSocket endpoint receives a message and session ID
2. **Intent Classification**: The orchestrator determines the appropriate agent
3. **Context Enhancement**: User message is enriched with conversation history and state
4. **Agent Processing**: Specialized agent processes the message with context
5. **State Update**: Response and new information are stored in the state
6. **Response Streaming**: Response is streamed back to the user

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

### Adding New Agents or Tools

To add new agents or tools, follow these steps:

1. Create a new agent file in the `agents` directory
2. Define any tools as Python functions with proper docstrings
3. Create an Agent instance with the tools
4. Import the agent in the appropriate files and add it to the agent selection logic

### Future Improvements

1. **NLP-Based Entity Extraction**: Replace simple keyword matching with ML-based entity extraction
2. **User Preference Learning**: Improve tracking and learning of user preferences over time
3. **Personalization**: Enhance recommendations based on user history and preferences
4. **Multi-Language Support**: Expand support for multiple languages
5. **Context Compression**: Implement more sophisticated context summarization techniques
6. **Machine Learning Classification**: Replace rule-based classification with ML model for better accuracy
7. **Multi-Intent Support**: Handle queries that span multiple intents by utilizing multiple agents
8. **Enhanced Agent Specialization**: Add more specialized agents for accommodation, transportation, etc.

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
