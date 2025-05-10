# Travel Agent Backend using Google ADK

This is the backend application for the Travel Agent project, which provides AI-powered travel planning services using Google's Agent Development Kit (ADK).

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Google Cloud project with Vertex AI enabled
- Google API Key (for local development)

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

3. Edit the `.env` file and add your configuration:

```
# For local development with Google AI Studio
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=your_api_key_here

# For deployment with Vertex AI
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_CLOUD_PROJECT_NUMBER=your_project_number
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_STORAGE_BUCKET=your_bucket_name
GOOGLE_GENAI_MODEL=gemini-1.5-pro-001
```

### Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the server:

```bash
# From the backend directory
python main.py
```

The server will run on `http://localhost:8000` by default (configurable in the `.env` file).

## Architecture Overview

The project uses Google's Agent Development Kit (ADK) to implement a multi-agent system for travel planning:

1. **Root Agent**: Orchestrates the specialized agents and handles the initial user interaction
2. **Accommodation Agent**: Recommends hotels and other lodging options
3. **Activity Agent**: Suggests activities and attractions
4. **Restaurant Agent**: Provides dining recommendations
5. **Transportation Agent**: Advises on travel methods and logistics
6. **Travel Planner Agent**: Creates comprehensive travel plans using input from all other agents

## Project Structure

The backend is organized in the ADK pattern:

- `/agent.py` - Root agent definition
- `/root_agent_prompt.py` - Instructions for the root agent
- `/sub_agents/` - Specialized agent implementations
- `/tools/` - Tool functions that agents can use
- `/shared_libraries/` - Common utilities and helpers
- `/api/` - FastAPI endpoints and WebSocket handlers
- `/deployment/` - Scripts for deploying to Vertex AI Agent Engine

## Development

### Local Development

For local development, set `GOOGLE_GENAI_USE_VERTEXAI=0` in your `.env` file and provide a valid Google API Key.

To run the development server:

```bash
python main.py
```

To use the ADK command line tools:

```bash
# Run the agent
adk run .

# Use the web UI
adk web .
```

### Deployment to Agent Engine

To deploy the agent to Google Agent Engine:

1. Build the package:

```bash
poetry build --format=wheel --output=deployment
```

2. Deploy to Agent Engine:

```bash
cd deployment
python deploy.py --create
```

Once deployed, you can test it using the provided test script:

```bash
export RESOURCE_ID=your_resource_id
export USER_ID=your_user_id
python test_deployment.py --resource_id=$RESOURCE_ID --user_id=$USER_ID
```

## API Endpoints

The backend provides the following endpoints:

- `/api/ws/{session_id}`: WebSocket endpoint for real-time communication with the agent
- `/api/health`: Health check endpoint

## Troubleshooting

- **API Key Issues**: Make sure your Google API Key or Vertex AI credentials are valid
- **Import Errors**: Make sure all dependencies are installed correctly
- **Connection Issues**: Check if the server is running and the ports are not blocked

## License

This project is licensed under the Apache License 2.0
