# Tavily Search Integration for Travel A2A

This document explains how the Tavily search integration works in the Travel A2A application and how to use it effectively.

## Overview

Tavily is a search API that provides real-time, up-to-date information from the web. We've integrated it with our activity agent to enhance recommendations with current information about attractions, events, and activities in Thailand.

## Setup Requirements

1. **API Key**: You need a Tavily API key to use this feature. Get one from [https://tavily.com/](https://tavily.com/).

2. **Environment Variable**: Set the API key in your environment:
   ```bash
   # Add to your .env file
   TAVILY_API_KEY=your_tavily_api_key_here
   
   # Or export directly (for temporary use)
   export TAVILY_API_KEY=your_tavily_api_key_here
   ```

3. **Dependencies**: The integration requires these packages:
   ```bash
   pip install langchain>=0.1.0 langchain-community>=0.1.0 tavily-python>=0.2.8
   ```

## How It Works

The Tavily integration is set up in two modes:

1. **ADK Mode**: When using Google's Agent Development Kit (GOOGLE_GENAI_USE_VERTEXAI=1), Tavily is integrated as a tool that the activity agent can use automatically to search for information.

2. **Direct API Mode**: When using the direct Gemini API (GOOGLE_GENAI_USE_VERTEXAI=0), you can call the `activity_tavily_search` function directly from your code to search for information.

## Testing the Integration

Run the test script to verify that Tavily is working correctly:

```bash
cd /Users/wattanachaiprakobdee/Desktop/travel-a2a/backend
python scripts/test_tavily.py
```

For a more comprehensive example of how to use Tavily in your agent:

```bash
python scripts/tavily_agent_helper.py
```

## Using Tavily in Direct API Mode

Import the search function from the activity agent:

```python
from sub_agents.activity_agent import activity_tavily_search

# Simple search
results = activity_tavily_search("popular beaches in Thailand")

# Location-specific search
results = activity_tavily_search("best hiking trails", location="Phuket")
```

## Example Use Cases

1. **Finding current attraction details**:
   ```python
   info = activity_tavily_search("Grand Palace Bangkok opening hours ticket price 2025")
   ```

2. **Discovering seasonal events**:
   ```python
   events = activity_tavily_search("festivals and events", location="Chiang Mai")
   ```

3. **Checking for new attractions**:
   ```python
   new_places = activity_tavily_search("newly opened attractions in 2025", location="Phuket")
   ```

## Troubleshooting

If you encounter issues with the Tavily integration:

1. Check that the TAVILY_API_KEY is set correctly
2. Verify that all dependencies are installed
3. Look for errors in the logs (console output or tavily_debug.log)
4. Run the test script to isolate any issues

### Debug Logs

The integration creates detailed logs in:
- `tavily_debug.log` - Detailed debug information about Tavily operations
- `travel_a2a.log` - General application logs

## Performance Considerations

- Tavily search calls consume API quota and may add latency to responses
- Use searches judiciously for specific information needs
- Consider caching frequently requested information

## Enhancement Ideas

- Add caching for search results to reduce API calls
- Implement more specialized search functions for different types of activities
- Create a feedback mechanism to improve search quality over time
