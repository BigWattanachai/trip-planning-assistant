import React from 'react';
import { useTripPlanning } from '@/context/TripPlanningContext';
import ActivitiesSection from './ActivitiesSection';
import RestaurantsSection from './RestaurantsSection';
import FlightsSection from './FlightsSection';
import VideosSection from './VideosSection';
import AccommodationSection from './AccommodationSection';
import { Loader2 } from 'lucide-react';

interface CanvasProps {
  isPlanning: boolean;
}

const Canvas: React.FC<CanvasProps> = ({ isPlanning }) => {
  const { state } = useTripPlanning();

  return (
    <div className="h-full overflow-y-auto">
      {!state.tripData && !isPlanning && (
        <div className="h-full flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">Welcome to Travel Planner</h2>
            <p className="text-gray-600 mb-4">Start planning your perfect trip by providing your travel details.</p>
            <div className="w-64 h-64 mx-auto">
              <img
                src="/travel-illustration.svg"
                alt="Travel planning illustration"
                className="w-full h-full object-contain"
              />
            </div>
          </div>
        </div>
      )}

      {isPlanning && !state.tripData && (
        <div className="h-full flex items-center justify-center">
          <div className="text-center">
            <Loader2 className="w-12 h-12 text-primary-500 animate-spin mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Planning Your Trip</h2>
            <p className="text-gray-600">Our AI agents are working together to create your perfect itinerary...</p>
          </div>
        </div>
      )}

      {state.tripData && (
        <div className="space-y-6 p-6">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Your Trip to {state.tripData.destination}</h1>
            <p className="text-lg text-gray-600 mt-2">
              {state.tripData.startDate} to {state.tripData.endDate}
            </p>
          </div>

          <ActivitiesSection activities={state.tripData.activities} />
          <RestaurantsSection restaurants={state.tripData.restaurants} />
          <FlightsSection flights={state.tripData.flights} />
          <VideosSection videos={state.tripData.videos} />
          <AccommodationSection accommodations={state.tripData.accommodations} />
        </div>
      )}
    </div>
  );
};

export default Canvas;
