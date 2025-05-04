'use client';

import React, { createContext, useContext, useReducer, ReactNode } from 'react';

interface Activity {
  id: string;
  name: string;
  description: string;
  rating: number;
  openingHours: string;
  imageUrl: string;
  category: string;
}

interface Restaurant {
  id: string;
  name: string;
  cuisine: string;
  priceRange: string;
  rating: number;
  reviewHighlight: string;
  imageUrl: string;
}

interface Flight {
  id: string;
  airline: string;
  flightNumber: string;
  departure: {
    airport: string;
    time: string;
    date: string;
  };
  arrival: {
    airport: string;
    time: string;
    date: string;
  };
  duration: string;
  price: number;
  class: string;
  bookingUrl: string;
}

interface Video {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  embedUrl: string;
  duration: string;
  viewCount: string;
}

interface Accommodation {
  id: string;
  name: string;
  type: string;
  rating: number;
  reviewCount: number;
  price: number;
  priceUnit: string;
  amenities: string[];
  imageUrl: string;
  platform: 'Airbnb' | 'Agoda' | 'TripAdvisor';
  bookingUrl: string;
}

interface TripData {
  destination: string;
  departure: string;
  startDate: string;
  endDate: string;
  budget: string;
  activities: Activity[];
  restaurants: Restaurant[];
  flights: Flight[];
  videos: Video[];
  accommodations: Accommodation[];
}

interface TripPlanningState {
  tripData: TripData | null;
  isLoading: boolean;
  error: string | null;
}

type TripPlanningAction =
  | { type: 'SET_TRIP_DATA'; payload: TripData }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null };

const initialState: TripPlanningState = {
  tripData: null,
  isLoading: false,
  error: null,
};

const tripPlanningReducer = (
  state: TripPlanningState,
  action: TripPlanningAction
): TripPlanningState => {
  switch (action.type) {
    case 'SET_TRIP_DATA':
      return { ...state, tripData: action.payload, isLoading: false, error: null };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    default:
      return state;
  }
};

const TripPlanningContext = createContext<{
  state: TripPlanningState;
  dispatch: React.Dispatch<TripPlanningAction>;
} | undefined>(undefined);

export const TripPlanningProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(tripPlanningReducer, initialState);

  return (
    <TripPlanningContext.Provider value={{ state, dispatch }}>
      {children}
    </TripPlanningContext.Provider>
  );
};

export const useTripPlanning = () => {
  const context = useContext(TripPlanningContext);
  if (context === undefined) {
    throw new Error('useTripPlanning must be used within a TripPlanningProvider');
  }
  return context;
};
