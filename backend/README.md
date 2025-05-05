# Travel Planner API

This is the backend API for the AI-powered Travel Planner application, built using FastAPI and Google's Agent Development Kit (ADK).

## Features

- Flight search recommendations
- Accommodation search
- Restaurant and dining recommendations
- Activity and attraction suggestions
- Travel-related YouTube video curation
- Comprehensive travel plan generation

## System Architecture

The backend is composed of specialized AI agents, each focused on a specific aspect of travel planning:

1. **ActivitySearchAgent**: Finds activities and attractions at destinations
2. **RestaurantAgent**: Recommends dining options based on preferences
3. **FlightSearchAgent**: Provides flight recommendations and information
4. **AccommodationAgent**: Suggests lodging options at destinations
5. **YouTubeVideoAgent**: Curates relevant travel videos
6. **TravelCoordinator**: Main agent that orchestrates all others to create a cohesive travel plan

## Prerequisites

- Python 3.9+
- pip (Python package manager)
- Google API Key for the Gemini API

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/travel-planner.git
   cd travel-planner/backend
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

4. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file to add your Google API key

## Running the Application

### Development mode

```bash
uvicorn main:app --reload
```

### Production mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Using Docker

```bash
docker build -t travel-planner-api .
docker run -p 8000:8000 travel-planner-api
```

## API Endpoints

The API is structured around the following resource groups:

- `/api/activities` - Activity and attraction recommendations
- `/api/restaurants` - Dining recommendations
- `/api/flights` - Flight search and information
- `/api/accommodations` - Lodging recommendations
- `/api/videos` - Travel video curation
- `/api/travel-plans` - Comprehensive travel planning

### Key Endpoints

- `POST /api/travel-plans/create` - Create a comprehensive travel plan
- `POST /api/travel-plans/destination-insights` - Get insights about a destination
- `POST /api/activities/search` - Search for activities at a destination
- `POST /api/restaurants/search` - Search for restaurants at a destination
- `POST /api/flights/search` - Search for flight options
- `POST /api/accommodations/search` - Search for accommodation options
- `POST /api/videos/search` - Search for travel videos

## Documentation

Once the server is running, the API documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DEBUG | Enable debug mode | True |
| API_PREFIX | Prefix for all API routes | /api |
| DEFAULT_MODEL | Default Gemini model for agents | gemini-1.5-flash |
| COORDINATOR_MODEL | Model for the coordinator agent | gemini-1.5-pro |
| GOOGLE_API_KEY | Your Google API key | - |
| CORS_ORIGINS | Allowed CORS origins | * |
| ENABLE_CACHE | Enable response caching | True |
| CACHE_TTL | Cache time-to-live in seconds | 3600 |

## Development

The backend is structured as follows:

- `/agents` - Specialized AI agents for different travel aspects
- `/config` - Application configuration
- `/routers` - FastAPI route handlers
- `/schemas` - Pydantic models for request/response validation
- `/tools` - Utility functions and tools

## License

This project is licensed under the MIT License - see the LICENSE file for details.
