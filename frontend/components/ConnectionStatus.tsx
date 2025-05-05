"use client";

import React from 'react';
import { useWebSocket } from './WebSocketProvider';

const ConnectionStatus = () => {
  const { isConnected, connectionError } = useWebSocket();
  
  if (isConnected) {
    return null; // Don't show anything when connected
  }
  
  return (
    <div className="fixed bottom-4 right-4 p-3 bg-red-500 text-white rounded-md shadow-lg z-50">
      {connectionError || 'Connection lost. Reconnecting...'}
    </div>
  );
};

export default ConnectionStatus;
