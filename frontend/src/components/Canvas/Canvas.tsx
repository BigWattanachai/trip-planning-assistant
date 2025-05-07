import React, { useEffect } from 'react';
import { useTripPlanning } from '@/context/TripPlanningContext';
import ActivitiesSection from './ActivitiesSection';
import RestaurantsSection from './RestaurantsSection';
import FlightsSection from './FlightsSection';
import VideosSection from './VideosSection';
import AccommodationSection from './AccommodationSection';
import { Loader2, MapPin, Calendar, Users, Plane, MessageSquare } from 'lucide-react';
import { motion } from 'framer-motion';

interface CanvasProps {
  isPlanning: boolean;
}

const Canvas: React.FC<CanvasProps> = ({ isPlanning }) => {
  const { state } = useTripPlanning();

  // Add debug logging to help diagnose the issue
  useEffect(() => {
    console.log("Canvas component state:", {
      hasTripData: !!state.tripData,
      isPlanning,
      destination: state.tripData?.destination || "None",
      messagesCount: state.messages.length,
      hasUserMessages: state.messages.some(msg => msg.role === 'user'),
      renderWelcomeMessage: renderWelcomeMessage,
      renderChatOnly: renderChatOnly
    });
  }, [state.tripData, isPlanning, state.messages.length]);

  // Fade-in animation for sections
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.3
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6 }
    }
  };

  // Define rendering conditions
  // Only show welcome message if no trip data, not planning, and no user messages
  const renderWelcomeMessage = !state.tripData && !isPlanning && 
    (state.messages.length === 0 || (state.messages.length === 1 && state.messages[0].role === 'assistant'));

  const renderLoadingMessage = isPlanning && !state.tripData;
  const renderTripData = !!state.tripData;

  // Show chat messages when there are messages but no trip data and not in planning mode
  const renderChatOnly = !renderWelcomeMessage && !renderLoadingMessage && !renderTripData;

  return (
    <div className="h-full overflow-y-auto bg-gradient-to-b from-blue-50 to-white">
      {renderWelcomeMessage && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="h-full flex items-center justify-center"
        >
          <div className="text-center max-w-2xl mx-auto px-6">
            <div className="inline-block p-3 bg-blue-100 rounded-full mb-6">
              <Plane className="w-10 h-10 text-primary-500" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Welcome to Travel Planner</h2>
            <p className="text-gray-600 mb-8 text-lg">
              Start planning your perfect trip by providing your travel details xxxxx.
            </p>
            <p className="text-gray-500 mb-6">
              Simply use the chat interface on the right to tell us where you want to go, 
              or use the trip input form to provide your destination, dates, and budget.
            </p>
            <div className="w-80 h-80 mx-auto relative">
              <div className="absolute inset-0 bg-blue-500 rounded-full opacity-10 animate-pulse"></div>
              <img
                src="/travel-illustration.svg"
                alt="Travel planning illustration"
                className="w-full h-full object-contain relative z-10"
              />
            </div>
          </div>
        </motion.div>
      )}

      {renderChatOnly && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="h-full p-8"
        >
          <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Chat with our Travel Assistant</h2>
            <p className="text-gray-600 mb-4">
              You're chatting with our AI travel assistant. When you're ready to plan a trip, 
              just ask about planning a trip to your desired destination.
            </p>
          </div>

          {/* Chat Messages Section */}
          {state.messages.length > 0 && (
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <div className="flex items-center mb-6">
                <MessageSquare className="w-6 h-6 text-primary-500 mr-3" />
                <h2 className="text-2xl font-bold text-gray-900">Chat History</h2>
              </div>
              <div className="space-y-4">
                {state.messages.map((message) => (
                  <div 
                    key={message.id}
                    className={`p-4 rounded-lg ${
                      message.role === 'user' 
                        ? 'bg-primary-50 border-l-4 border-primary-500 ml-8' 
                        : 'bg-gray-50 border-l-4 border-gray-300 mr-8'
                    }`}
                  >
                    <div className="flex items-center mb-2">
                      <div 
                        className={`w-8 h-8 rounded-full flex items-center justify-center mr-2 ${
                          message.role === 'user' ? 'bg-primary-500' : 'bg-gray-500'
                        }`}
                      >
                        <span className="text-white text-xs font-bold">
                          {message.role === 'user' ? 'You' : 'AI'}
                        </span>
                      </div>
                      <span className="text-xs text-gray-500">
                        {new Date(message.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-gray-700 whitespace-pre-wrap">{message.content}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}

      {renderLoadingMessage && (
        <div className="h-full flex items-center justify-center">
          <div className="text-center max-w-lg mx-auto p-8 rounded-2xl bg-white shadow-lg">
            <div className="relative">
              <Loader2 className="w-16 h-16 text-primary-500 animate-spin mx-auto mb-6" />
              <div className="absolute inset-0 bg-primary-100 rounded-full opacity-30 scale-150 animate-ping"></div>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Crafting Your Dream Itinerary</h2>
            <p className="text-gray-600 text-lg mb-4">Our AI agents are collaborating to design your perfect trip experience...</p>
            <div className="grid grid-cols-3 gap-3 mt-6">
              <div className="text-center p-2 rounded-lg bg-blue-50">
                <p className="text-xs text-gray-500">Finding Activities</p>
                <div className="w-full h-1 bg-gray-200 mt-1 overflow-hidden rounded-full">
                  <div className="h-full bg-blue-500 rounded-full animate-pulse" style={{width: '60%'}}></div>
                </div>
              </div>
              <div className="text-center p-2 rounded-lg bg-amber-50">
                <p className="text-xs text-gray-500">Researching Dining</p>
                <div className="w-full h-1 bg-gray-200 mt-1 overflow-hidden rounded-full">
                  <div className="h-full bg-amber-500 rounded-full animate-pulse" style={{width: '40%'}}></div>
                </div>
              </div>
              <div className="text-center p-2 rounded-lg bg-green-50">
                <p className="text-xs text-gray-500">Planning Routes</p>
                <div className="w-full h-1 bg-gray-200 mt-1 overflow-hidden rounded-full">
                  <div className="h-full bg-green-500 rounded-full animate-pulse" style={{width: '75%'}}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {renderTripData && state.tripData && (
        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="p-8"
        >
          <motion.div 
            variants={itemVariants}
            className="mb-10 bg-white rounded-2xl shadow-lg p-8 relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-64 h-64 bg-primary-100 rounded-full -translate-y-1/2 translate-x-1/4 opacity-70"></div>
            <div className="relative z-10">
              <h1 className="text-4xl font-extrabold text-gray-900 mb-3">
                Your Journey to {state.tripData.destination}
              </h1>
              <div className="flex flex-wrap gap-4 text-lg text-gray-600 mt-3 mb-6">
                <div className="flex items-center">
                  <Calendar className="w-5 h-5 text-primary-500 mr-2" />
                  <span>{state.tripData.startDate} to {state.tripData.endDate}</span>
                </div>
                {state.tripData.travelers && (
                  <div className="flex items-center">
                    <Users className="w-5 h-5 text-primary-500 mr-2" />
                    <span>{state.tripData.travelers} travelers</span>
                  </div>
                )}
                {state.tripData.budget && (
                  <div className="flex items-center">
                    <span className="w-5 h-5 text-primary-500 mr-2 font-bold">฿</span>
                    <span>Budget: {state.tripData.budget}</span>
                  </div>
                )}
              </div>

              <p className="text-lg text-gray-700 leading-relaxed max-w-3xl">
                Welcome to your personalized travel experience in {state.tripData.destination}! 
                We've curated an exceptional itinerary featuring stunning attractions, 
                authentic dining experiences, and comfortable accommodations tailored to your preferences.
                Explore below to discover the highlights of your upcoming adventure.
              </p>
            </div>
          </motion.div>

          <motion.div variants={itemVariants}>
            <ActivitiesSection activities={state.tripData.activities} />
          </motion.div>

          <motion.div variants={itemVariants}>
            <RestaurantsSection restaurants={state.tripData.restaurants} />
          </motion.div>

          <motion.div variants={itemVariants}>
            <FlightsSection flights={state.tripData.flights} />
          </motion.div>

          <motion.div variants={itemVariants}>
            <VideosSection videos={state.tripData.videos} />
          </motion.div>

          <motion.div variants={itemVariants}>
            <AccommodationSection accommodations={state.tripData.accommodations} />
          </motion.div>

          {/* Chat Messages Section */}
          {state.messages.length > 0 && (
            <motion.div variants={itemVariants}>
              <div className="mt-10 bg-white rounded-2xl shadow-lg p-8">
                <div className="flex items-center mb-6">
                  <MessageSquare className="w-6 h-6 text-primary-500 mr-3" />
                  <h2 className="text-2xl font-bold text-gray-900">Chat History</h2>
                </div>
                <div className="space-y-4">
                  {state.messages.map((message) => (
                    <div 
                      key={message.id}
                      className={`p-4 rounded-lg ${
                        message.role === 'user' 
                          ? 'bg-primary-50 border-l-4 border-primary-500 ml-8' 
                          : 'bg-gray-50 border-l-4 border-gray-300 mr-8'
                      }`}
                    >
                      <div className="flex items-center mb-2">
                        <div 
                          className={`w-8 h-8 rounded-full flex items-center justify-center mr-2 ${
                            message.role === 'user' ? 'bg-primary-500' : 'bg-gray-500'
                          }`}
                        >
                          <span className="text-white text-xs font-bold">
                            {message.role === 'user' ? 'You' : 'AI'}
                          </span>
                        </div>
                        <span className="text-xs text-gray-500">
                          {new Date(message.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-gray-700 whitespace-pre-wrap">{message.content}</p>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </motion.div>
      )}
    </div>
  );
};

export default Canvas;
