import React, {useState, useRef, useEffect} from 'react';
import {Send, Bot, User, Loader, WifiOff} from 'lucide-react';
import {useTripPlanning} from '@/context/TripPlanningContext';
import {TripData, Message} from '@/context/TripPlanningContext';
import WebSocketService from '@/services/WebSocketService';
import TripInputForm from './TripInputForm';

interface ChatInterfaceProps {
    onPlanningStart: () => void;
    onPlanningComplete: () => void;
}

// Helper function to create sample trip data
const createSampleTripData = (tripInput?: any): TripData => {
    const destination = tripInput?.destination || "Bangkok";
    const departure = tripInput?.departure || "No departure specified";
    const startDate = tripInput?.startDate || "2023-05-10";
    const endDate = tripInput?.endDate || "2023-05-15";
    const budget = tripInput?.budgetRange || "฿30,000";

    return {
        destination,
        departure,
        startDate,
        endDate,
        budget,
    };
};

// Helper function to parse trip data from AI response
const extractTripDataFromResponse = (messages: Message[]): TripData | null => {
    try {
        // Look for messages that might contain structured trip data
        const assistantMessages = messages.filter(msg => msg.role === 'assistant');
        if (assistantMessages.length === 0) return null;

        console.log("Looking for trip data in assistant messages:", assistantMessages.length);

        // Check for JSON data in the message
        const jsonRegex = /```json\s*({[\s\S]*?})\s*```/;

        // Try to find JSON blocks in the message content
        for (let i = assistantMessages.length - 1; i >= 0; i--) {
            const message = assistantMessages[i];
            const jsonMatch = message.content.match(jsonRegex);

            if (jsonMatch && jsonMatch[1]) {
                try {
                    const jsonStr = jsonMatch[1].trim();
                    console.log("Found JSON data:", jsonStr.substring(0, 100) + "...");
                    const parsedData = JSON.parse(jsonStr);

                    // Check if it has the expected structure
                    if (parsedData.destination &&
                        (parsedData.activities || parsedData.restaurants ||
                            parsedData.flights || parsedData.accommodations)) {
                        console.log("Successfully parsed TripData from JSON");
                        return parsedData as TripData;
                    }
                } catch (error) {
                    console.error("Error parsing JSON from message:", error);
                }
            }
        }

        // If no JSON found, try to extract structured data from text
        const lastMessage = assistantMessages[assistantMessages.length - 1].content;
        console.log("Trying to extract trip data from text:", lastMessage.substring(0, 100) + "...");

        // Check for common patterns in the text
        const destinationMatch = lastMessage.match(/(?:เที่ยว|ไป|ท่องเที่ยว)\s*(?:ที่|ยัง)?\s*([^,\.\n]+)/i);

        if (destinationMatch) {
            // If we found a destination, create a sample trip data with that destination
            return createSampleTripData({ destination: destinationMatch[1].trim() });
        }

        return null;
    } catch (error) {
        console.error("Error extracting trip data:", error);
        return null;
    }
};

const ChatInterface: React.FC<ChatInterfaceProps> = ({onPlanningStart, onPlanningComplete}) => {
    // Use context for messages
    const {dispatch, state} = useTripPlanning();

    // Initialize messages in context if empty
    useEffect(() => {
        if (state.messages.length === 0) {
            dispatch({
                type: 'SET_MESSAGES',
                payload: []
            });
        }
    }, []);
    const [inputValue, setInputValue] = useState('');
    const [isConnected, setIsConnected] = useState(false);
    const [isConnecting, setIsConnecting] = useState(false);
    const [connectionError, setConnectionError] = useState<string | null>(null);
    const [currentMessageId, setCurrentMessageId] = useState<string | null>(null);
    const [isPlanningTrip, setIsPlanningTrip] = useState(false);
    const [processingTimer, setProcessingTimer] = useState<NodeJS.Timeout | null>(null);
    const [isProcessingMessage, setIsProcessingMessage] = useState(false);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const wsRef = useRef<WebSocketService | null>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({behavior: 'smooth'});
    };

    useEffect(() => {
        scrollToBottom();
    }, [state.messages]);

    // Connect to WebSocket when component mounts
    useEffect(() => {
        connectToWebSocket();

        // Clean up on unmount
        return () => {
            disconnectWebSocket();
        };
    }, []);

    // Clear any timers on unmount
    useEffect(() => {
        return () => {
            if (processingTimer) {
                clearTimeout(processingTimer);
            }
        };
    }, [processingTimer]);

    // Process messages to look for trip data
    useEffect(() => {
        if (!isPlanningTrip) return;

        console.log("Planning trip state is active, checking for trip data...");
        console.log("Current state of tripData:", state.tripData ? "Has Data" : "No Data");

        // Look for trip data in the messages
        const tripData = extractTripDataFromResponse(state.messages);

        if (tripData) {
            console.log("Setting trip data to context:", tripData.destination);
            dispatch({type: 'SET_TRIP_DATA', payload: tripData});
            dispatch({type: 'SET_LOADING', payload: false});
            onPlanningComplete();
            setIsPlanningTrip(false);

            // Clear any pending timer
            if (processingTimer) {
                clearTimeout(processingTimer);
                setProcessingTimer(null);
            }
        }
    }, [state.messages, isPlanningTrip, dispatch, onPlanningComplete, state.tripData, processingTimer]);

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
                // Set isProcessingMessage to false when we receive the first message
                setIsProcessingMessage(false);

                console.log("Received message from agent:", text.substring(0, 50) + "...");
                console.log("Current message ID:", currentMessageId);

                // For a new message from the agent
                if (currentMessageId === null) {
                    console.log("Creating new message");
                    const newMessageId = Date.now().toString();
                    setCurrentMessageId(newMessageId);

                    const newMessage = {
                        id: newMessageId,
                        role: 'assistant' as const,
                        content: text,
                        timestamp: new Date(),
                    };

                    dispatch({
                        type: 'ADD_MESSAGE',
                        payload: newMessage
                    });
                } else {
                    console.log("Appending to existing message:", currentMessageId);
                    // For streaming response, append to existing message
                    const updatedMessages = state.messages.map(msg =>
                        msg.id === currentMessageId
                            ? {...msg, content: msg.content + text}
                            : msg
                    );

                    dispatch({
                        type: 'SET_MESSAGES',
                        payload: updatedMessages
                    });
                }
            },
            onTurnComplete: () => {
                console.log("Turn complete handler called, resetting currentMessageId", currentMessageId);
                setCurrentMessageId(null);
                setIsProcessingMessage(false);

                // If we're planning a trip, try to extract trip data after turn is complete
                if (isPlanningTrip) {
                    console.log("Turn complete, checking messages for trip data");
                    const tripData = extractTripDataFromResponse(state.messages);
                    if (tripData) {
                        console.log("Found trip data after turn completion");
                        dispatch({type: 'SET_TRIP_DATA', payload: tripData});
                        dispatch({type: 'SET_LOADING', payload: false});
                        onPlanningComplete();
                        setIsPlanningTrip(false);
                    }
                }
            },
            onInterrupted: () => {
                setCurrentMessageId(null);
            },
            onClose: () => {
                setIsConnected(false);
                setIsProcessingMessage(false);
                console.log('WebSocket disconnected');
            },
            onError: (error: any) => {
                setConnectionError('Connection to the assistant failed. Please try again.');
                setIsConnecting(false);
                setIsConnected(false);
                setIsProcessingMessage(false);
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

        // Check if the message is for trip planning
        const isTripPlanningQuery = inputValue.toLowerCase().includes('วางแผนการเดินทาง') ||
            inputValue.toLowerCase().includes('ไปเที่ยว') ||
            inputValue.toLowerCase().includes('plan a trip');

        if (isTripPlanningQuery) {
            setIsPlanningTrip(true);
            onPlanningStart();
            dispatch({type: 'SET_LOADING', payload: true});

            // Set a timer to use sample data if no results after 10 seconds
            if (processingTimer) {
                clearTimeout(processingTimer);
            }

            const timer = setTimeout(() => {
                console.log("Timer expired, forcing trip data update with sample data");
                const tripData = extractTripDataFromResponse(state.messages) || createSampleTripData();
                dispatch({type: 'SET_TRIP_DATA', payload: tripData});
                dispatch({type: 'SET_LOADING', payload: false});
                onPlanningComplete();
                setIsPlanningTrip(false);
            }, 10000);

            setProcessingTimer(timer);
        }

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: inputValue,
            timestamp: new Date(),
        };

        dispatch({
            type: 'ADD_MESSAGE',
            payload: userMessage
        });

        // Set processing message state to true
        setIsProcessingMessage(true);

        // Send message to WebSocket
        if (wsRef.current) {
            try {
                wsRef.current.sendMessage(inputValue);
            } catch (error) {
                console.error('Failed to send message:', error);
                setConnectionError('Failed to send message. Please try again.');
                setIsProcessingMessage(false);
                if (isTripPlanningQuery) {
                    dispatch({type: 'SET_LOADING', payload: false});
                    onPlanningComplete();
                    setIsPlanningTrip(false);

                    if (processingTimer) {
                        clearTimeout(processingTimer);
                        setProcessingTimer(null);
                    }
                }
            }
        } else {
            setConnectionError('Not connected to the assistant. Please refresh the page.');
            setIsProcessingMessage(false);
            if (isTripPlanningQuery) {
                dispatch({type: 'SET_LOADING', payload: false});
                onPlanningComplete();
                setIsPlanningTrip(false);

                if (processingTimer) {
                    clearTimeout(processingTimer);
                    setProcessingTimer(null);
                }
            }
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

        setIsPlanningTrip(true);
        onPlanningStart();
        dispatch({type: 'SET_LOADING', payload: true});

        // Clear any existing timer
        if (processingTimer) {
            clearTimeout(processingTimer);
        }

        // Set a timer to use sample data if no results
        const timer = setTimeout(() => {
            console.log("Trip input timer expired, forcing update with sample data");
            const sampleTripData = createSampleTripData(tripInput);
            dispatch({type: 'SET_TRIP_DATA', payload: sampleTripData});
            dispatch({type: 'SET_LOADING', payload: false});
            onPlanningComplete();
            setIsPlanningTrip(false);
        }, 10000);

        setProcessingTimer(timer);

        const tripQueryText = `ช่วยวางแผนการเดินทางท่องเที่ยวแบบละเอียดที่สุด ตามเงื่อนไขต่อไปนี้ :\n- ต้นทาง: ${tripInput.departure}\n- ปลายทาง: ${tripInput.destination}\n- ช่วงเวลาเดินทาง: วันที่: ${tripInput.startDate} ถึงวันที่ ${tripInput.endDate}\n- งบประมาณรวม: ${tripInput.budgetRange}
      \nสิ่งที่ต้องการให้ระบุในแผนการเดินทาง:

      - รายละเอียดการเดินทางไป-กลับ (เช่น รถยนต์, เครื่องบิน, รถทัวร์ พร้อมเวลาเดินทางและราคาค่าโดยสาร)\n
      - สถานที่ท่องเที่ยวสำคัญที่ควรแวะชมในแต่ละวัน (เน้นสถานที่สำคัญทางวัฒนธรรม ธรรมชาติ และจุดถ่ายรูปยอดนิยม)\n
      - ที่พักแนะนำ (เน้นที่พักคุณภาพดี ราคาคุ้มค่า ทำเลสะดวก พร้อมราคาต่อคืน)\n
      - ร้านอาหารแนะนำ (ระบุชื่อร้าน ประเภทอาหาร เมนูเด็ดที่ต้องลอง และราคาคร่าวๆ ต่อมื้อ)\n
      - กิจกรรมที่น่าสนใจห้ามพลาดใน ${tripInput.destination} (เช่น เที่ยวชมวัด ปั่นจักรยาน วิถีชุมชน ชมวิว ถ่ายภาพ)\n
      แจกแจงค่าใช้จ่ายแต่ละวันให้ชัดเจน (รวมยอดค่าใช้จ่ายทั้งหมดไม่เกินงบที่ระบุไว้ ${tripInput.budgetRange}) \n

      แนะนำเคล็ดลับหรือข้อควรระวัง เพื่อให้การเดินทางสะดวก ปลอดภัย และประทับใจมากที่สุด

      ขอผลลัพธ์ในรูปแบบที่อ่านเข้าใจง่าย ชัดเจน พร้อมจัดตารางให้ดูสวยงามและใช้งานง่ายที่สุด
    `;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: tripQueryText,
            timestamp: new Date(),
        };

        dispatch({
            type: 'ADD_MESSAGE',
            payload: userMessage
        });

        // Set processing message state to true
        setIsProcessingMessage(true);

        // Send the trip planning request to the backend via WebSocket
        if (wsRef.current) {
            try {
                wsRef.current.sendMessage(tripQueryText);
            } catch (error) {
                console.error('Failed to send trip planning request:', error);
                setConnectionError('Failed to send trip planning request. Please try again.');
                setIsProcessingMessage(false);

                // Still use the sample data to show something
                setTimeout(() => {
                    const tripData = extractTripDataFromResponse(state.messages) || createSampleTripData(tripInput);
                    dispatch({type: 'SET_TRIP_DATA', payload: tripData});
                    dispatch({type: 'SET_LOADING', payload: false});
                    onPlanningComplete();
                    setIsPlanningTrip(false);
                }, 2000);

                if (processingTimer) {
                    clearTimeout(processingTimer);
                    setProcessingTimer(null);
                }
            }
        } else {
            setConnectionError('Not connected to the assistant. Please refresh the page.');
            setIsProcessingMessage(false);

            // Still use the sample data to show something
            setTimeout(() => {
                const tripData = extractTripDataFromResponse(state.messages) || createSampleTripData(tripInput);
                dispatch({type: 'SET_TRIP_DATA', payload: tripData});
                dispatch({type: 'SET_LOADING', payload: false});
                onPlanningComplete();
                setIsPlanningTrip(false);
            }, 2000);

            if (processingTimer) {
                clearTimeout(processingTimer);
                setProcessingTimer(null);
            }
        }
    };

    return (
        <div className="h-full flex flex-col bg-gray-50">
            <div className="bg-white border-b border-gray-200 p-4">
                <div className="flex justify-between items-center">
                    <h2 className="text-lg font-semibold text-gray-900">AI Chat Assistant</h2>
                    {isConnecting ? (
                        <div className="flex items-center text-amber-600 text-sm">
                            <Loader className="w-4 h-4 mr-1 animate-spin"/>
                            <span>Connecting...</span>
                        </div>
                    ) : isConnected ? (
                        <div className="flex items-center text-green-600 text-sm">
                            <div className="w-2 h-2 rounded-full bg-green-500 mr-1"></div>
                            <span>Connected</span>
                        </div>
                    ) : (
                        <div className="flex items-center text-rose-600 text-sm">
                            <WifiOff className="w-4 h-4 mr-1"/>
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

                <TripInputForm onSubmit={handleTripInputSubmit}/>

                {state.messages.map((message) => (
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
                                    <User className="w-5 h-5 text-white"/>
                                ) : (
                                    <Bot className="w-5 h-5 text-gray-600"/>
                                )}
                            </div>
                            <div
                                className={`rounded-lg px-4 py-2 ${
                                    message.role === 'user'
                                        ? 'bg-primary-500 text-white'
                                        : 'bg-white border border-gray-200'
                                }`}
                            >
                                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
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

                {isProcessingMessage && (
                    <div className="flex justify-center my-4">
                            <div className="flex items-center space-x-2">
                                <div className="w-2 h-2 rounded-full bg-primary-400 animate-pulse"></div>
                                <div className="w-2 h-2 rounded-full bg-primary-500 animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                                <div className="w-2 h-2 rounded-full bg-primary-600 animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                                <span className="text-sm font-medium text-primary-700">Processing your request</span>
                                <div className="w-2 h-2 rounded-full bg-primary-400 animate-pulse"></div>
                                <div className="w-2 h-2 rounded-full bg-primary-500 animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                                <div className="w-2 h-2 rounded-full bg-primary-600 animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                            </div>
                    </div>
                )}

                <div ref={messagesEndRef}/>
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
                        <Send className="w-5 h-5"/>
                    </button>
                </div>
            </form>
        </div>
    );
};

export default ChatInterface;
