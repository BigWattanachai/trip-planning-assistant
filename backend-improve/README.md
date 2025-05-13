# Travel A2A Backend (Improved)

This is an improved version of the Travel A2A backend with the following enhancements:

- Support for both Vertex AI (Google ADK) mode and Direct API mode
- Integration with Tavily Search for all sub-agents to provide up-to-date information
- Better error handling and state management
- Enhanced logging and debugging information

## Architecture

The backend follows a modular architecture:

```
backend-improve/
├── api/                      # API endpoints and handlers
│   ├── __init__.py
│   ├── async_agent_handler.py
│   └── routes.py
├── core/                     # Core functionality
│   ├── __init__.py
│   └── state_manager.py
├── shared_libraries/         # Shared functionality
│   ├── __init__.py
│   └── callbacks.py
├── sub_agents/               # Specialized agents
│   ├── __init__.py
│   ├── activity_agent.py     # With Tavily search integration
│   └── ... 
├── tools/                    # Tools used by agents
│   ├── __init__.py
│   ├── store_state.py
│   └── tavily_search.py      # Tavily Search integration
├── __init__.py               # Package initialization
├── agent.py                  # Root agent definition
├── main.py                   # Entry point
├── requirements.txt          # Dependencies
└── root_agent_prompt.py      # Root agent prompt
```

## Key Features

### 1. Dual Mode Support

The backend can operate in two modes:

- **Vertex AI (ADK) Mode**: Uses Google's Agent Development Kit for advanced agent capabilities
- **Direct API Mode**: Uses the Gemini API directly with simulated sub-agents

The mode is determined by the `GOOGLE_GENAI_USE_VERTEXAI` environment variable.

### 2. Tavily Search Integration

All sub-agents can now use Tavily Search to retrieve up-to-date information:

- In ADK mode, Tavily is integrated as a LangChain tool via the `LangchainTool` wrapper
- In Direct API mode, Tavily search is available through the `search_with_tavily` function

### 3. Enhanced Error Handling

The backend includes robust error handling to:

- Recover from API errors
- Provide informative error messages
- Fall back to alternative methods when primary methods fail

### 4. Improved State Management

The `StateManager` class provides:

- Conversation history tracking
- Session state storage
- Support for both ADK and Direct API modes

## Setup and Configuration

### Environment Variables

- `GOOGLE_GENAI_USE_VERTEXAI`: Set to "1" for Vertex AI mode, "0" for Direct API mode
- `GOOGLE_GENAI_MODEL`: Gemini model to use (default: "gemini-2.0-flash")
- `GOOGLE_API_KEY`: Required for Direct API mode
- `TAVILY_API_KEY`: Required for Tavily Search integration

### Installation

```bash
pip install -r requirements.txt
```

### Running the Backend

```bash
python main.py
```

## API Endpoints

- `GET /`: Root endpoint with API information
- `GET /health`: Health check endpoint
- `GET /info`: Detailed backend information
- `WebSocket /ws/{session_id}`: WebSocket endpoint for real-time communication

## Using Tavily Search

To enable Tavily Search:

1. Get a Tavily API key from [https://tavily.com/](https://tavily.com/)
2. Add it to your `.env` file: `TAVILY_API_KEY=your_api_key_here`

Tavily Search will then be used to enhance responses with up-to-date information.
