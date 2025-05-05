"use client";

import React, { createContext, useContext, useEffect, useState, useRef } from 'react';

// Define the shape of the context
type WebSocketContextType = {
  isConnected: boolean;
  connectionError: string | null;
  // Add any other properties your WebSocket context needs
  sendMessage?: (message: any) => void;
};

// Create the context with a default value
const WebSocketContext = createContext<WebSocketContextType>({
  isConnected: false,
  connectionError: null,
});

// Hook to use the WebSocket context
export const useWebSocket = () => useContext(WebSocketContext);

export const WebSocketProvider = ({ children }: { children: React.ReactNode }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const webSocketRef = useRef<WebSocket | null>(null);
  
  useEffect(() => {
    const connectWebSocket = () => {
      // Generate a random client ID
      const clientId = Math.random().toString(36).substring(2, 15);
      const ws = new WebSocket(`ws://localhost:8000/api/ws/${clientId}`);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setConnectionError(null);
      };
      
      ws.onclose = (event) => {
        console.log('WebSocket disconnected', event);
        setIsConnected(false);
        // Try to reconnect after a delay
        setTimeout(connectWebSocket, 3000);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionError('Connection error occurred. Trying to reconnect...');
      };
      
      // ...existing code...
      
      webSocketRef.current = ws;
      
      // Cleanup function
      return () => {
        ws.close();
      };
    };
    
    connectWebSocket();
    
    // Cleanup on component unmount
    return () => {
      if (webSocketRef.current) {
        webSocketRef.current.close();
      }
    };
  }, []);
  
  // Function to send messages to the server
  const sendMessage = (message: any) => {
    if (webSocketRef.current && webSocketRef.current.readyState === WebSocket.OPEN) {
      webSocketRef.current.send(JSON.stringify(message));
    } else {
      console.error("WebSocket is not connected");
      setConnectionError("Connection lost. Unable to send message.");
    }
  };
  
  return (
    <WebSocketContext.Provider value={{ 
      isConnected, 
      connectionError,
      sendMessage,
    }}>
      {children}
    </WebSocketContext.Provider>
  );
};

