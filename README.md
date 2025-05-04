# Travel Planner with Google A2A and MCP Tools

A modern web application for planning trips using AI agents built with Google A2A architecture and MCP tools.

## Features

- 🤖 Multiple specialized AI agents working together
- 🎯 Activities and attractions recommendations
- 🍽️ Restaurant suggestions based on budget
- ✈️ Flight search and booking options
- 🎥 YouTube travel videos
- 🏨 Accommodation recommendations from multiple platforms
- 💬 Interactive chat interface
- 🎨 Beautiful, responsive UI

## Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **AI Integration**: Google Gemma-3, MCP Tools
- **State Management**: React Context
- **Icons**: Lucide React

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/yourusername/travel-a2a.git
cd travel-a2a
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Project Structure

```
travel-a2a/
├── src/
│   ├── app/              # Next.js app router
│   ├── components/       # React components
│   │   ├── Canvas/       # Travel results display
│   │   ├── Chat/         # Chat interface
│   │   └── Layout/       # Layout components
│   ├── context/          # React context providers
│   ├── services/         # AI agents and orchestration
│   │   └── agents/       # Individual AI agents
│   └── lib/              # Utility functions
├── public/               # Static assets
└── package.json          # Project dependencies
```

## AI Agents

The application uses multiple specialized AI agents:

1. **Activity Agent**: Finds activities and attractions
2. **Restaurant Agent**: Recommends dining options
3. **Flight Agent**: Searches for flight options
4. **Video Agent**: Curates relevant YouTube content
5. **Accommodation Agent**: Finds hotels and rentals

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google ADK for AI agent framework
- MCP Tools for context management
- Next.js team for the amazing framework
- Tailwind CSS for styling utilities
