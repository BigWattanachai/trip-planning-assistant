# Enhanced Multi-Agent Travel System

This document provides an overview of the enhanced multi-agent architecture for the travel planning assistant, inspired by the Google ADK design principles.

## Architecture Overview

The system uses a multi-agent approach with the following components:

1. **State Manager**: Central repository for maintaining conversation state and user context
2. **Improved Agent Orchestrator**: Coordinates between specialized agents, handling context-aware routing
3. **Itinerary Manager**: Manages travel itinerary creation and modification
4. **Specialized Agents**: Domain-specific agents for different aspects of travel planning

## Key Components

### State Manager

The `state_manager` maintains a rich context for each conversation, including:

- User profile and preferences
- Travel itinerary details
- Conversation history
- Detected entities (locations, dates, activities, foods)
- Previous agent interactions

This allows agents to access prior context and maintain continuity across agent handoffs.

### Improved Agent Orchestrator

The `improved_orchestrator` handles:

- Intent classification with context awareness
- Routing messages to appropriate specialized agents
- Enhancing user messages with relevant context
- Facilitating agent transitions

### Itinerary Manager

The `itinerary_manager` provides ADK-style itinerary management:

- Creating and updating itineraries
- Adding flights, visits, accommodations to itineraries
- Retrieving current day and event information

### Enhanced Agent Instructions

Each agent type has specialized instructions that:

- Define their specific responsibilities and domain
- Guide how they should handle context from previous interactions
- Provide instructions for cross-agent awareness

## Agent Flow

1. **User Message Received**: WebSocket endpoint receives a message and session ID
2. **Intent Classification**: `improved_orchestrator` determines the appropriate agent
3. **Context Enhancement**: User message is enriched with conversation history and state
4. **Agent Processing**: Specialized agent processes the message with context
5. **State Update**: Response and new information are stored in the state
6. **Response Streaming**: Response is streamed back to the user

## Specialized Agents

### Travel Agent (root_agent)

- General travel planning and orchestration
- Handles queries that don't clearly fit into other categories
- Maintains awareness of other specialized agents

### Activity Search Agent

- Specializes in finding activities and attractions
- Provides detailed information about things to do
- Aware of user interests and previous preferences

### Restaurant Agent

- Specializes in food and dining recommendations
- Considers dietary preferences and restrictions
- Can suggest culinary experiences based on location

## State Management

The state management approach is inspired by ADK's state model, with specialized tools for:

- **Memorization**: Storing key-value pairs in the session state
- **Entity Recognition**: Extracting locations, activities, and preferences
- **Context Summarization**: Creating concise summaries of relevant context
- **Follow-up Detection**: Identifying follow-up questions to maintain context

## Implementation Details

### Context-Aware Intent Classification

The system improves intent classification by considering:

- Conversation history
- Previous agent interactions
- Detected entities from prior messages
- Follow-up patterns

### Enhanced Message Processing

When processing messages, the system:

1. Stores the user message in conversation history
2. Extracts and stores entities from the message
3. Determines intent using context-aware classification
4. Enriches the user message with relevant context
5. Selects and uses the appropriate specialized agent
6. Stores the agent's response in the state

### Agent Handoff

When transitioning between agents, the system:

1. Tracks the previous and current agent in the state
2. Provides context summaries to the new agent
3. Includes relevant information from previous interactions
4. Maintains continuity in the conversation

## Future Improvements

1. **NLP-Based Entity Extraction**: Replace simple keyword matching with ML-based entity extraction
2. **User Preference Learning**: Improve tracking and learning of user preferences over time
3. **Personalization**: Enhance recommendations based on user history and preferences
4. **Multi-Language Support**: Expand support for multiple languages
5. **Context Compression**: Implement more sophisticated context summarization techniques

## Usage

To use the enhanced multi-agent system:

1. The WebSocket endpoint receives user messages
2. The system determines the appropriate agent type
3. The message is enhanced with relevant context
4. The agent processes the message and generates a response
5. The response is streamed back to the user

## Example Interaction Flow

```
[User]: Can you recommend some activities in Bangkok?

[System]:
1. Classifies intent as "activity"
2. Routes to activity_search_agent
3. Enhances message with context
4. Returns activity recommendations

[User]: What about good food there?

[System]:
1. Detects this is a follow-up question about food
2. Classifies intent as "restaurant"
3. Includes Bangkok context from previous message
4. Routes to restaurant_agent
5. Returns restaurant recommendations
```
