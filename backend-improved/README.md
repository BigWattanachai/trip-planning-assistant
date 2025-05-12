# Travel Agent Backend

A travel planning assistant built using Google's ADK (Agent Development Kit) best practices. This backend supports both direct API mode and Vertex AI mode with ADK.

## Features

- **Agent Team Architecture**: Root agent with specialized sub-agents for different travel aspects
- **State Management**: Remembers user preferences and travel details across the conversation
- **Dual Mode Support**: Works with both direct Gemini API and Vertex AI with ADK
- **Enhanced Search**: Integrates with Tavily for web search and YouTube for video insights
- **WebSocket API**: Real-time communication with frontend clients

## Sub-Agents

- **Accommodation Agent**: Recommends hotels, resorts, hostels based on location and budget
- **Activity Agent**: Suggests attractions, activities, and things to do
- **Restaurant Agent**: Recommends dining options and local cuisine
- **Transportation Agent**: Provides travel routes, methods, and costs
- **Travel Planner Agent**: Creates comprehensive travel itineraries

## Requirements

- Python 3.9+
- Google API Key (for direct mode) or Google Cloud Vertex AI access (for ADK mode)
- Optional: Tavily API Key and YouTube API Key for enhanced search capabilities

## Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd travel-a2a/backend-improved
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Edit the `.env` file with your API keys and configuration.

## Running the Application

### Direct API Mode

This mode uses Google's Generative AI API directly (Gemini models):

```bash
python main.py
```

### Vertex AI Mode with ADK

To use Google's Agent Development Kit with Vertex AI:

1. Set `GOOGLE_GENAI_USE_VERTEXAI=1` in your `.env` file
2. Ensure you've set up Google Cloud credentials
3. Run the application:

```bash
python main.py
```

## API Endpoints

- **WebSocket**: `/api/ws/{session_id}` - Main endpoint for real-time agent interaction
- **Health Check**: `/api/health` - Simple health check endpoint

## Architecture

The backend follows Google's ADK best practices with a clear separation of components:

- **Root Agent**: Orchestrates and delegates to specialized sub-agents
- **Sub-Agents**: Specialized agents for different travel aspects
- **Tools**: Reusable functions available to agents (search, state management)
- **Session Management**: Maintains conversation context and user preferences
- **API Routes**: WebSocket and HTTP endpoints for client communication

## Environment Variables

- `GOOGLE_API_KEY`: Required for direct API mode
- `GOOGLE_GENAI_MODEL`: Model to use (default: "gemini-2.0-flash")
- `GOOGLE_GENAI_USE_VERTEXAI`: Set to "1" to use Vertex AI with ADK
- `TAVILY_API_KEY`: Optional, for enhanced search capabilities
- `YOUTUBE_API_KEY`: Optional, for video insights
- See `.env.example` for all configuration options

## License

[Your License Information]
