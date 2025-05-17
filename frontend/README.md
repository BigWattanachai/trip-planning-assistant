# Trip Planning Assistant Frontend

This is the frontend application for the Trip Planning Assistant project, which connects to the backend AI travel planning service.

## Getting Started

### Prerequisites

- Node.js 18.x or later
- npm or yarn
- Backend service running (see backend README.md)

### Environment Setup

Create a `.env.local` file in the root directory with the following content:

```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Adjust the URL if your backend is running on a different host or port.

### Installation

1. Install dependencies:

```bash
npm install
# or
yarn install
```

2. Start the development server:

```bash
npm run dev
# or
yarn dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Features

- Real-time chat with the AI travel planning assistant
- Trip planning form
- WebSocket connection to the backend for streaming responses
- Visualization of travel recommendations including:
  - Activities
  - Restaurants
  - Flights
  - Accommodations
  - Travel videos

## Architecture

The frontend uses:

- Next.js for the React framework
- TypeScript for type safety
- WebSocket for real-time communication with the AI backend
- Tailwind CSS for styling
- Context API for state management

## Connecting to the Backend

The frontend connects to the backend using WebSockets for the chat interface. The connection is established when the chat component mounts. The WebSocket connection enables:

1. Real-time streaming of AI responses
2. Bidirectional communication
3. Turn management (knowing when the AI has completed its response)

Additionally, REST API endpoints are used for specific functionality like retrieving travel recommendations, searching for activities, etc.

## Troubleshooting

- **Connection Issues**: Make sure the backend server is running and accessible at the URL specified in your `.env.local` file.
- **WebSocket Errors**: Check the browser console for detailed error messages. The application will attempt to reconnect automatically if the connection is lost.
- **Missing Data**: If travel recommendations aren't showing up, check the browser console for API errors.

## Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add some amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request
