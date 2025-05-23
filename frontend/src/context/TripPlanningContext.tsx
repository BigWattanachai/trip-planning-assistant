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
  location: string;
  price: string;
  highlights: string[] ;
  bestTimeToVisit: string;
}

interface Restaurant {
  id: string;
  name: string;
  cuisine: string;
  priceRange: string;
  rating: number;
  reviewHighlight: string;
  imageUrl: string;
  location: string;
  hours: string;
  reservationRequired: boolean;
  specialties: string[];
}

interface Flight {
  id: string;
  airline: string;
  flightNumber: string;
  departure: {
    airport: string;
    time: string;
    date: string;
    terminal: string;
  };
  arrival: {
    airport: string;
    time: string;
    date: string;
    terminal: string;
  };
  duration: string;
  price: number;
  stops: number;
  class: string;
  bookingUrl: string;
  layover: string;
  cancellationPolicy: string;
  amenities: string[];
}

interface Video {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  embedUrl: string;
  duration: string;
  viewCount: string;
  likes: string;
  channel: string;
  publishDate: string;
}

export interface Accommodation {
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
  location: string;
  description: string;
  distance: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface TripData {
  destination: string;
  departure: string;
  startDate: string;
  endDate: string;
  budget: string;
}

interface TripPlanningState {
  tripData: TripData | null;
  isLoading: boolean;
  error: string | null;
  messages: Message[];
}

type TripPlanningAction =
  | { type: 'SET_TRIP_DATA'; payload: TripData }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'SET_MESSAGES'; payload: Message[] };

const initialState: TripPlanningState = {
  tripData: null,
  isLoading: false,
  error: null,
  messages: [],
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
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.payload] };
    case 'SET_MESSAGES':
      return { ...state, messages: action.payload };
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
