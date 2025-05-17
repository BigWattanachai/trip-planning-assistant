# Trip Planning Assistant

**AI-powered Travel Planning Platform**

---

## Overview
Trip Planning Assistant is an advanced travel agent app that leverages the latest AI models (Google Gemini, Vertex AI, and more) to help users plan trips, discover destinations, and get real insights from YouTube travel content. It features a modular backend, a modern Next.js frontend, and seamless integration with Google and YouTube APIs.

---

## Features
- **AI Travel Planning:** Generate personalized itineraries and recommendations using Gemini or Vertex AI (Direct API & ADK modes).
- **YouTube Insight Agent:** Extract travel wisdom directly from YouTube videos, including sentiment, popular channels, and transcript analysis.
- **Destination Search & Activities:** Find accommodations, activities, and hidden gems.
- **Modern UI:** Fast, responsive, and mobile-friendly frontend built with Next.js and TailwindCSS.
- **Extensible Agent Architecture:** Add new agents/tools for more travel domains.

---

## Architecture
```
[ Next.js Frontend ]  <->  [ FastAPI Backend (Python) ]  <->  [ Google APIs | YouTube | Vertex AI | Tavily ]
```
- **Frontend:** `/frontend` (Next.js, React, TailwindCSS)
- **Backend:** `/backend` (FastAPI, ADK, LangChain, Google APIs)
- **Docker Compose:** Orchestrates both services for local/dev deployment

---

## Quick Start (Docker Compose)
1. **Clone the repo:**
   ```sh
   git clone https://github.com/BigWattanachai/trip-planning-assistant.git

   cd trip-planning-assistant
   ```
2. **Configure Environment:**
    - Edit `.env` in the root directory with your Google/YouTube API keys and settings.
3. **Build and Run:**
   ```sh
   docker-compose up --build
   ```
    - Frontend: [http://localhost:3000](http://localhost:3000)
    - Backend: [http://localhost:8000](http://localhost:8000)

---

## Manual Setup (Development)
### Backend
```sh
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Frontend
```sh
cd frontend
npm install
npm run build && npm start
```

---

## Environment Variables (`.env`)
- `GOOGLE_API_KEY` — Google Cloud/YouTube API key
- `YOUTUBE_API_KEY` — YouTube Data API key
- `GOOGLE_GENAI_USE_VERTEXAI` — `0` for Direct API, `1` for Vertex AI (ADK)
- `GOOGLE_GENAI_MODEL` — Model name (e.g., `gemini-2.0-flash`)
- `GOOGLE_CLOUD_PROJECT`, `VERTEX_LOCATION` — Vertex AI settings (if using Vertex)
- `PORT`, `HOST` — Backend server settings

> **Tip:** All services now use the root `.env` file for configuration.

---

## Key Components
### Backend
- **FastAPI**: Main API framework
- **Google Gemini/Vertex AI**: AI model integration
- **YouTube Insight Agent**: Extracts travel insights from YouTube
- **LangChain, Tavily**: Search and language tools
- **ADK Mode**: Advanced session management, streaming responses

### Frontend
- **Next.js**: Modern React framework
- **TailwindCSS**: Styling
- **API Integration**: Connects to backend for AI and travel data

---

## Usage
- Access the frontend at [http://localhost:3000](http://localhost:3000)
- Plan trips, search destinations, and get AI-powered insights
- Use the YouTube tab to extract travel wisdom from real videos

---

## Contributing
1. Fork the repo
2. Create a feature branch
3. Submit a pull request with clear description

---

## License
MIT

---

## Credits
- Built with [FastAPI](https://fastapi.tiangolo.com/), [Next.js](https://nextjs.org/), [Google Gemini](https://ai.google.dev/), [YouTube Data API](https://developers.google.com/youtube/v3), [LangChain](https://python.langchain.com/), and more.

---

## Contact
For questions, issues, or feature requests, please open an issue or contact the maintainer.

## Acknowledgments

- Google ADK for AI agent framework
- MCP Tools for context management
- Next.js team for the amazing framework
- Tailwind CSS for styling utilities
