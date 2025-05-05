/**
 * ApiService: Handles API requests to the backend
 */
import axios from 'axios';

// Get the backend URL from environment variables or use default
const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

const ApiService = {
  /**
   * Make a GET request to the backend API
   */
  get: async (endpoint: string, params = {}) => {
    try {
      const response = await axios.get(`${API_BASE_URL}${endpoint}`, { params });
      return response.data;
    } catch (error) {
      console.error(`Error making GET request to ${endpoint}:`, error);
      throw error;
    }
  },

  /**
   * Make a POST request to the backend API
   */
  post: async (endpoint: string, data = {}) => {
    try {
      const response = await axios.post(`${API_BASE_URL}${endpoint}`, data);
      return response.data;
    } catch (error) {
      console.error(`Error making POST request to ${endpoint}:`, error);
      throw error;
    }
  },

  /**
   * Health check to verify backend connectivity
   */
  healthCheck: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/health`);
      return response.data.status === 'healthy';
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  },

  /**
   * Plan a trip using the backend API
   */
  planTrip: async (tripData: {
    origin: string;
    destination: string;
    departure_date: string;
    return_date: string;
    budget?: string;
    interests?: string;
    travelers?: number;
  }) => {
    return ApiService.post('/api/plan_trip', tripData);
  },

  /**
   * Search for activities in a location
   */
  searchActivities: async (params: {
    location: string;
    preferences?: string;
    budget?: string;
  }) => {
    return ApiService.get('/api/search_activities', params);
  },

  /**
   * Search for restaurants in a location
   */
  searchRestaurants: async (params: {
    location: string;
    cuisine?: string;
    budget?: string;
    dietary_restrictions?: string;
  }) => {
    return ApiService.get('/api/search_restaurants', params);
  },

  /**
   * Search for flights between two locations
   */
  searchFlights: async (params: {
    origin: string;
    destination: string;
    departure_date: string;
    return_date?: string;
    passengers?: number;
    cabin_class?: string;
  }) => {
    return ApiService.get('/api/search_flights', params);
  },

  /**
   * Search for accommodations in a location
   */
  searchAccommodations: async (params: {
    location: string;
    check_in_date: string;
    check_out_date: string;
    guests?: number;
    room_type?: string;
    amenities?: string;
    budget?: string;
  }) => {
    return ApiService.get('/api/search_accommodations', params);
  },

  /**
   * Search for travel-related videos about a destination
   */
  searchTravelVideos: async (params: {
    destination: string;
    content_type?: string;
  }) => {
    return ApiService.get('/api/search_travel_videos', params);
  },
};

export default ApiService;
