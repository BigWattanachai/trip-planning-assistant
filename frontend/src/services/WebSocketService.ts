/**
 * WebSocketService: Manages WebSocket connections to the backend
 */

interface WebSocketMessage {
  message?: string;
  turn_complete?: boolean;
  interrupted?: boolean;
}

interface WebSocketHandlers {
  onMessage: (text: string) => void;
  onTurnComplete: () => void;
  onInterrupted?: () => void;
  onError: (error: any) => void;
  onOpen?: () => void;
  onClose?: () => void;
}

class WebSocketService {
  private socket: WebSocket | null = null;
  private sessionId: string;
  private backendUrl: string;
  private handlers: WebSocketHandlers;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout: NodeJS.Timeout | null = null;

  constructor(sessionId: string, handlers: WebSocketHandlers) {
    this.sessionId = sessionId;
    this.handlers = handlers;
    
    // Get backend URL from environment or use default
    this.backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    
    // Convert http(s) to ws(s)
    const wsProtocol = this.backendUrl.startsWith('https') ? 'wss' : 'ws';
    this.backendUrl = this.backendUrl.replace(/^http(s?):\/\//, `${wsProtocol}://`);
  }

  connect(): void {
    try {
      // Create WebSocket connection
      const wsUrl = `${this.backendUrl}/api/ws/${this.sessionId}`;
      this.socket = new WebSocket(wsUrl);

      // Setup event handlers
      this.socket.onopen = this.handleOpen.bind(this);
      this.socket.onmessage = this.handleMessage.bind(this);
      this.socket.onclose = this.handleClose.bind(this);
      this.socket.onerror = this.handleError.bind(this);
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.handlers.onError(error);
    }
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
  }

  sendMessage(text: string): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(text);
    } else {
      console.error('WebSocket is not connected');
      this.handlers.onError(new Error('WebSocket is not connected'));
    }
  }

  private handleOpen(event: Event): void {
    console.log('WebSocket connection established');
    this.reconnectAttempts = 0;
    if (this.handlers.onOpen) {
      this.handlers.onOpen();
    }
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const data: WebSocketMessage = JSON.parse(event.data);
      
      if (data.message) {
        this.handlers.onMessage(data.message);
      }
      
      if (data.turn_complete) {
        this.handlers.onTurnComplete();
      }
      
      if (data.interrupted && this.handlers.onInterrupted) {
        this.handlers.onInterrupted();
      }
    } catch (error) {
      console.error('Error processing WebSocket message:', error);
      this.handlers.onError(error);
    }
  }

  private handleClose(event: CloseEvent): void {
    console.log(`WebSocket connection closed: ${event.code} ${event.reason}`);
    
    // Attempt to reconnect if not intentionally closed
    if (event.code !== 1000) {
      this.attemptReconnect();
    }
    
    if (this.handlers.onClose) {
      this.handlers.onClose();
    }
  }

  private handleError(event: Event): void {
    console.error('WebSocket error:', event);
    this.handlers.onError(event);
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      
      console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      this.reconnectTimeout = setTimeout(() => {
        console.log(`Reconnecting... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect();
      }, delay);
    } else {
      console.error('Maximum reconnect attempts reached');
      this.handlers.onError(new Error('Maximum reconnect attempts reached'));
    }
  }
}

export default WebSocketService;
