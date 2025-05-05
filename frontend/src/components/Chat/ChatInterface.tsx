import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader, WifiOff } from 'lucide-react';
import { useTripPlanning } from '@/context/TripPlanningContext';
import { TripData } from '@/context/TripPlanningContext';
import WebSocketService from '@/services/WebSocketService';
import TripInputForm from './TripInputForm';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  onPlanningStart: () => void;
  onPlanningComplete: () => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ onPlanningStart, onPlanningComplete }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'สวัสดีค่ะ! ฉันคือผู้ช่วยวางแผนการเดินทางของคุณ บอกฉันหน่อยว่าคุณอยากไปเที่ยวที่ไหน และมีงบประมาณเท่าไหร่คะ?',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [currentMessageId, setCurrentMessageId] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocketService | null>(null);

  const { dispatch } = useTripPlanning();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // Connect to WebSocket when component mounts
  useEffect(() => {
    connectToWebSocket();
    
    // Clean up on unmount
    return () => {
      disconnectWebSocket();
    };
  }, []);
  
  const connectToWebSocket = () => {
    if (wsRef.current) {
      return; // Already connected or connecting
    }
    
    setIsConnecting(true);
    setConnectionError(null);
    
    // Generate a unique session ID
    const sessionId = Math.random().toString(36).substring(2, 15);
    
    // Create WebSocket handlers
    const handlers = {
      onOpen: () => {
        setIsConnected(true);
        setIsConnecting(false);
        console.log('WebSocket connected');
      },
      onMessage: (text: string) => {
        // For a new message from the agent
        if (currentMessageId === null) {
          const newMessageId = Date.now().toString();
          setCurrentMessageId(newMessageId);
          
          setMessages(prev => [
            ...prev,
            {
              id: newMessageId,
              role: 'assistant',
              content: text,
              timestamp: new Date(),
            }
          ]);
        } else {
          // For streaming response, append to existing message
          setMessages(prev => 
            prev.map(msg => 
              msg.id === currentMessageId 
                ? { ...msg, content: msg.content + text } 
                : msg
            )
          );
        }
      },
      onTurnComplete: () => {
        setCurrentMessageId(null);
      },
      onInterrupted: () => {
        setCurrentMessageId(null);
      },
      onClose: () => {
        setIsConnected(false);
        console.log('WebSocket disconnected');
      },
      onError: (error: any) => {
        setConnectionError('Connection to the assistant failed. Please try again.');
        setIsConnecting(false);
        setIsConnected(false);
        console.error('WebSocket error:', error);
      }
    };
    
    // Create and connect the WebSocket
    wsRef.current = new WebSocketService(sessionId, handlers);
    wsRef.current.connect();
  };
  
  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.disconnect();
      wsRef.current = null;
      setIsConnected(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    
    // Check if WebSocket is connected
    if (!isConnected) {
      if (!isConnecting) {
        connectToWebSocket();
      }
      setConnectionError('Connecting to the assistant. Please try again in a moment.');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    
    // Send message to WebSocket
    if (wsRef.current) {
      try {
        wsRef.current.sendMessage(inputValue);
      } catch (error) {
        console.error('Failed to send message:', error);
        setConnectionError('Failed to send message. Please try again.');
      }
    } else {
      setConnectionError('Not connected to the assistant. Please refresh the page.');
    }
    
    setInputValue('');
  };

  const handleTripInputSubmit = async (tripInput: any) => {
    // Check if WebSocket is connected
    if (!isConnected) {
      if (!isConnecting) {
        connectToWebSocket();
      }
      setConnectionError('Connecting to the assistant. Please try again in a moment.');
      return;
    }
    
    onPlanningStart();
    dispatch({ type: 'SET_LOADING', payload: true });

    const tripQueryText = `วางแผนการเดินทางให้หน่อย:\n- จาก: ${tripInput.departure}\n- ไป: ${tripInput.destination}\n- วันที่: ${tripInput.startDate} ถึง ${tripInput.endDate}\n- งบประมาณ: ${tripInput.budgetRange}`;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: tripQueryText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);

    // Send the trip planning request to the backend via WebSocket
    if (wsRef.current) {
      try {
        wsRef.current.sendMessage(tripQueryText);
      } catch (error) {
        console.error('Failed to send trip planning request:', error);
        setConnectionError('Failed to send trip planning request. Please try again.');
        dispatch({ type: 'SET_LOADING', payload: false });
        onPlanningComplete();
      }
    } else {
      setConnectionError('Not connected to the assistant. Please refresh the page.');
      dispatch({ type: 'SET_LOADING', payload: false });
      onPlanningComplete();
    }
    
    // For demo purposes, we'll still use the mock data since the real backend might not have
    // full functionality yet. In a production environment, this data would come from the backend.
    // We'll use a timeout to simulate backend processing
    setTimeout(() => {
      // This is mock data - in a real implementation, the trip data would be parsed from the agent's response
      const tripData: TripData = {
        destination: tripInput.destination,
        departure: tripInput.departure,
        startDate: tripInput.startDate,
        endDate: tripInput.endDate,
        budget: tripInput.budgetRange,
        activities: [
          {
            id: '1',
            name: 'วัดพระแก้ว',
            description: 'วัดที่มีชื่อเสียงที่สุดในกรุงเทพฯ เป็นที่ประดิษฐานพระแก้วมรกต',
            rating: 4.8,
            openingHours: '8:30 AM - 3:30 PM',
            imageUrl: 'https://images.unsplash.com/photo-1563492065599-3520f775eeed?w=800&auto=format&fit=crop&q=60',
            category: 'Cultural',
          },
          {
            id: '2',
            name: 'ตลาดนัดจตุจักร',
            description: 'ตลาดนัดที่ใหญ่ที่สุดในประเทศไทย มีสินค้ามากกว่า 15,000 ร้านค้า',
            rating: 4.5,
            openingHours: 'Sat-Sun: 9:00 AM - 6:00 PM',
            imageUrl: 'https://images.unsplash.com/photo-1577719996642-edf11c65fe76?w=800&auto=format&fit=crop&q=60',
            category: 'Shopping',
          },
        ],
        restaurants: [
          {
            id: '1',
            name: 'ร้านทิพย์สมัย ผัดไทยประตูผี',
            cuisine: 'Thai',
            priceRange: '฿฿',
            rating: 4.7,
            reviewHighlight: 'ผัดไทยที่ดีที่สุดในกรุงเทพฯ รสชาติต้นตำรับ',
            imageUrl: 'https://images.unsplash.com/photo-1559314809-0d155014e29e?w=800&auto=format&fit=crop&q=60',
          },
          {
            id: '2',
            name: 'บ้านอาหารเรือนไทย',
            cuisine: 'Thai Fine Dining',
            priceRange: '฿฿฿',
            rating: 4.6,
            reviewHighlight: 'บรรยากาศสุดคลาสสิก อาหารไทยรสเลิศ',
            imageUrl: 'https://images.unsplash.com/photo-1543352634-a1c51d9f1fa7?w=800&auto=format&fit=crop&q=60',
          },
        ],
        flights: [
          {
            id: '1',
            airline: 'Thai Airways',
            flightNumber: 'TG102',
            departure: {
              airport: 'SFO',
              time: '23:55',
              date: tripInput.startDate,
            },
            arrival: {
              airport: 'BKK',
              time: '06:50+2',
              date: tripInput.startDate,
            },
            duration: '15h 55m',
            price: 29750, // Converted from $850 to ฿29,750
            class: 'Economy',
            bookingUrl: 'https://www.thaiairways.com',
          },
          {
            id: '2',
            airline: 'United Airlines',
            flightNumber: 'UA899',
            departure: {
              airport: 'SFO',
              time: '10:40',
              date: tripInput.startDate,
            },
            arrival: {
              airport: 'BKK',
              time: '18:30+1',
              date: tripInput.startDate,
            },
            duration: '17h 50m',
            price: 25200, // Converted from $720 to ฿25,200
            class: 'Economy',
            bookingUrl: 'https://www.united.com',
          },
        ],
        videos: [
          {
            id: '1',
            title: 'Bangkok Travel Guide - Best Things to Do',
            description: 'Complete guide to Bangkok covering temples, markets, food, and nightlife.',
            thumbnail: 'https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=800&auto=format&fit=crop&q=60',
            embedUrl: 'https://www.youtube.com/watch?v=example1',
            duration: '12:45',
            viewCount: '250K',
          },
          {
            id: '2',
            title: 'Street Food Tour in Bangkok',
            description: 'Discover the best street food in Bangkok with this comprehensive food tour.',
            thumbnail: 'https://images.unsplash.com/photo-1608060434411-0c67dca250bd?w=800&auto=format&fit=crop&q=60',
            embedUrl: 'https://www.youtube.com/watch?v=example2',
            duration: '15:30',
            viewCount: '180K',
          },
        ],
        accommodations: [
          {
            id: '1',
            name: 'The Siam Hotel',
            type: 'Luxury Hotel',
            rating: 4.9,
            reviewCount: 342,
            price: 8750, // Converted from $250 to ฿8,750
            priceUnit: 'night',
            amenities: ['WiFi', 'Pool', 'Private Bathroom', 'Breakfast'],
            imageUrl: 'https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=800&auto=format&fit=crop&q=60',
            platform: 'Agoda',
            bookingUrl: 'https://www.agoda.com',
          },
          {
            id: '2',
            name: 'Riva Surya Bangkok',
            type: 'Boutique Hotel',
            rating: 4.7,
            reviewCount: 567,
            price: 4200, // Converted from $120 to ฿4,200
            priceUnit: 'night',
            amenities: ['WiFi', 'River View', 'Fitness Center', 'Restaurant'],
            imageUrl: 'https://images.unsplash.com/photo-1581701391032-33cb5e4cff33?w=800&auto=format&fit=crop&q=60',
            platform: 'TripAdvisor',
            bookingUrl: 'https://www.tripadvisor.com',
          },
        ],
      };

      dispatch({ type: 'SET_TRIP_DATA', payload: tripData });
      dispatch({ type: 'SET_LOADING', payload: false });
      onPlanningComplete();
    }, 5000);
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-900">AI Chat Assistant</h2>
          {isConnecting ? (
            <div className="flex items-center text-amber-600 text-sm">
              <Loader className="w-4 h-4 mr-1 animate-spin" />
              <span>Connecting...</span>
            </div>
          ) : isConnected ? (
            <div className="flex items-center text-green-600 text-sm">
              <div className="w-2 h-2 rounded-full bg-green-500 mr-1"></div>
              <span>Connected</span>
            </div>
          ) : (
            <div className="flex items-center text-rose-600 text-sm">
              <WifiOff className="w-4 h-4 mr-1" />
              <span>Disconnected</span>
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {connectionError && (
          <div className="bg-rose-50 border border-rose-200 rounded-lg p-3 text-rose-600 text-sm">
            {connectionError}
          </div>
        )}
        
        <TripInputForm onSubmit={handleTripInputSubmit} />

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`flex gap-3 max-w-[80%] ${
                message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
              }`}
            >
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.role === 'user' ? 'bg-primary-500' : 'bg-gray-200'
                }`}
              >
                {message.role === 'user' ? (
                  <User className="w-5 h-5 text-white" />
                ) : (
                  <Bot className="w-5 h-5 text-gray-600" />
                )}
              </div>
              <div
                className={`rounded-lg px-4 py-2 ${
                  message.role === 'user'
                    ? 'bg-primary-500 text-white'
                    : 'bg-white border border-gray-200'
                }`}
              >
                <p className="text-sm">{message.content}</p>
                <p
                  className={`text-xs mt-1 ${
                    message.role === 'user' ? 'text-primary-200' : 'text-gray-500'
                  }`}
                >
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <button
            type="submit"
            className="bg-primary-500 text-white rounded-lg p-2 hover:bg-primary-600 transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;
