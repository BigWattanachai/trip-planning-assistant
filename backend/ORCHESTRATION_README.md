# Travel Agent Orchestration System

This document describes the multi-agent orchestration system implemented in the Travel A2A project.

## Overview

The orchestration system routes user queries to the appropriate specialized agent based on intent classification. This approach addresses the problem of sequential agents sending multiple overlapping responses.

## Components

### 1. Intent Classification

The system classifies user requests into three categories:
- **Restaurant Intent**: Queries about food, restaurants, dining, etc.
- **Activity Intent**: Queries about attractions, places to visit, things to do, etc.
- **General Travel Intent**: General queries or ambiguous requests

### 2. Agent Structure

Our system uses three main agents:
- **Root Agent (Orchestrator)**: Main entry point, handles general travel queries, and delegates to specialized agents.
- **Restaurant Agent**: Specialized agent for food and restaurant queries that uses restaurant-specific tools.
- **Activity Search Agent**: Specialized agent for attractions and activities that uses activity-specific tools.

### 3. WebSocket Communication

The WebSocket endpoints handle:
- Session management
- Intent classification
- Agent routing
- Response streaming

## Intent Classification Algorithm

The intent classification algorithm uses a weighted keyword matching approach:
1. Check for high-priority patterns (e.g., "ร้าน" + "อร่อย" for restaurant intent)
2. Count weighted occurrences of keywords from predefined lists
3. Apply special phrase boosts for particular expressions
4. Compare scores with thresholds to determine intent

The algorithm is specifically optimized for Thai language queries about travel destinations.

## Flow Diagram

```
User Query
    │
    ▼
Intent Classification
    │
    ├── Restaurant Intent ──► Restaurant Agent
    │
    ├── Activity Intent ───► Activity Search Agent
    │
    └── General Intent ────► Root Agent
    │
    ▼
Response Generation
    │
    ▼
WebSocket Response
```

## Benefits of This Approach

1. **Focused Responses**: Users receive focused responses from specialized agents rather than generic information.
2. **Single Response Strategy**: Only one agent responds to each query, preventing multiple overlapping responses.
3. **Optimized for Thai Language**: Intent classifier is optimized for both Thai and English queries.
4. **Stateful Conversations**: Session management maintains conversation context.

## Example Interactions

### Restaurant Intent Example
```
User: "ช่วยแนะนำร้านอาหารอร่อยๆ ที่น่านให้หน่อยได้ไหมคะ?"
System: [Classifies as restaurant intent]
Response: [Restaurant agent provides detailed restaurant recommendations]
```

### Activity Intent Example
```
User: "มีที่เที่ยวอะไรน่าสนใจในน่าน"
System: [Classifies as activity intent]
Response: [Activity agent provides detailed attraction recommendations]
```

### General Travel Intent Example
```
User: "ไปเที่ยวน่าน"
System: [May classify as general or activity depending on context]
Response: [Appropriate agent responds with general information or asks follow-up questions]
```

## Implementation Details

The intent classification is implemented in `agents/travel_agent.py`. Key functions:
- `classify_intent(user_input)`: Determines the intent type (restaurant, activity, or travel)
- The WebSocket handler in `main.py` uses this function to route requests

## Future Improvements

1. **Machine Learning Classification**: Replace rule-based classification with ML model for better accuracy
2. **Contextual Intent Detection**: Consider previous conversation context when classifying intent
3. **Multi-Intent Support**: Handle queries that span multiple intents by utilizing multiple agents
4. **Enhanced Agent Specialization**: Add more specialized agents for accommodation, transportation, etc.
5. **Agent Collaboration**: Allow agents to collaborate on complex queries that span multiple domains
