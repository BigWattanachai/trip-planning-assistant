# YouTube Tools for Travel Agent

This module provides YouTube search and transcript extraction functionality for the Travel Agent.

## Features

- Search for YouTube videos related to travel destinations
- Extract transcripts from YouTube videos
- Extract valuable travel insights from video content
- Generate formatted reports for agent consumption

## Setup

1. Get a YouTube Data API v3 key from the [Google Cloud Console](https://console.cloud.google.com/apis/library/youtube.googleapis.com)
2. Add your API key to the `.env` file:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key_here
   ```

## How It Works

The YouTube tools enhance the travel planning experience by:

1. Searching for relevant YouTube videos based on the destination
2. Extracting transcripts from the videos
3. Analyzing the content to extract valuable travel insights
4. Formatting the insights for inclusion in travel plans

## Integration

The YouTube tools integrate with both the ADK agent (via `youtube_search_tool`) and direct API mode (via `search_youtube_for_travel`).

### Example Usage

```python
# ADK mode (when GOOGLE_GENAI_USE_VERTEXAI=1)
youtube_results = youtube_search_tool(
    query="travel guide",
    destination="Chiang Mai",
    max_results=3,
    language="th"
)

# Direct API mode (when GOOGLE_GENAI_USE_VERTEXAI=0)
youtube_results = search_youtube_for_travel(
    query="travel guide",
    destination="Chiang Mai",
    max_results=3,
    language="th"
)

# Format insights for agent consumption
formatted_insights = format_youtube_insights_for_agent(youtube_results["insights"])
```

## Types of Insights Extracted

The YouTube tools extract the following types of insights:

- Popular places to visit
- Local tips from travelers
- Food recommendations
- Accommodation suggestions
- Transportation advice
- Cultural insights
- Activities and experiences

These insights are presented in a structured format that the agent can easily incorporate into its responses.
