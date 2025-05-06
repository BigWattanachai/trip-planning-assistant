"""
Itinerary Manager: Module for managing travel itineraries with ADK-inspired design
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from state_manager import state_manager

class ItineraryManager:
    """
    Manages travel itineraries with a structure similar to ADK's itinerary model.
    
    This class provides methods for creating, updating, and retrieving itineraries,
    as well as adding days and events to existing itineraries.
    """
    
    def __init__(self):
        """Initialize the itinerary manager"""
        # Define the default empty itinerary structure
        self._empty_itinerary = {
            "trip_name": "",
            "start_date": "",
            "end_date": "",
            "origin": "",
            "destination": "",
            "days": []
        }
    
    def create_itinerary(self, session_id: str, 
                       trip_name: str, 
                       origin: str, 
                       destination: str,
                       start_date: str, 
                       end_date: str) -> Dict[str, Any]:
        """
        Create a new itinerary for a session.
        
        Args:
            session_id: The session identifier
            trip_name: The name of the trip
            origin: The origin location
            destination: The destination location
            start_date: The start date in ISO format (YYYY-MM-DD)
            end_date: The end date in ISO format (YYYY-MM-DD)
            
        Returns:
            The newly created itinerary
        """
        # Create a new itinerary
        itinerary = self._empty_itinerary.copy()
        itinerary["trip_name"] = trip_name
        itinerary["origin"] = origin
        itinerary["destination"] = destination
        itinerary["start_date"] = start_date
        itinerary["end_date"] = end_date
        
        # Calculate the number of days
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        num_days = (end - start).days + 1
        
        # Create empty days
        for i in range(num_days):
            current_date = start + timedelta(days=i)
            itinerary["days"].append({
                "day_number": i + 1,
                "date": current_date.strftime("%Y-%m-%d"),
                "events": []
            })
        
        # Update the state
        state_manager.update_state(session_id, "itinerary", itinerary)
        
        # Also store individual fields for easier access
        state_manager.update_state(session_id, "origin", origin)
        state_manager.update_state(session_id, "destination", destination)
        state_manager.update_state(session_id, "start_date", start_date)
        state_manager.update_state(session_id, "end_date", end_date)
        state_manager.update_state(session_id, "itinerary_start_date", start_date)
        state_manager.update_state(session_id, "itinerary_end_date", end_date)
        
        return itinerary
    
    def get_itinerary(self, session_id: str) -> Dict[str, Any]:
        """
        Get the itinerary for a session.
        
        Args:
            session_id: The session identifier
            
        Returns:
            The itinerary
        """
        return state_manager.get_state(session_id).get("itinerary", self._empty_itinerary)
    
    def add_flight(self, session_id: str, 
                 day_number: int,
                 flight_number: str,
                 departure_airport: str,
                 arrival_airport: str,
                 departure_time: str,
                 arrival_time: str,
                 seat_number: str = "",
                 boarding_time: str = "",
                 price: str = "",
                 booking_id: str = "") -> Dict[str, Any]:
        """
        Add a flight event to the itinerary.
        
        Args:
            session_id: The session identifier
            day_number: The day number
            flight_number: The flight number
            departure_airport: The departure airport code
            arrival_airport: The arrival airport code
            departure_time: The departure time
            arrival_time: The arrival time
            seat_number: The seat number (optional)
            boarding_time: The boarding time (optional)
            price: The price (optional)
            booking_id: The booking ID (optional)
            
        Returns:
            The flight event
        """
        event = {
            "event_type": "flight",
            "description": f"Flight from {departure_airport} to {arrival_airport}",
            "flight_number": flight_number,
            "departure_airport": departure_airport,
            "arrival_airport": arrival_airport,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "booking_required": True
        }
        
        # Add optional fields if provided
        if seat_number:
            event["seat_number"] = seat_number
        if boarding_time:
            event["boarding_time"] = boarding_time
        if price:
            event["price"] = price
        if booking_id:
            event["booking_id"] = booking_id
        
        # Add the event to the itinerary
        self._add_event_to_day(session_id, day_number, event)
        
        return event
    
    def add_visit(self, session_id: str,
                day_number: int,
                description: str,
                location: Dict[str, str],
                start_time: str,
                end_time: str,
                booking_required: bool = False,
                booking_id: str = "") -> Dict[str, Any]:
        """
        Add a visit event to the itinerary.
        
        Args:
            session_id: The session identifier
            day_number: The day number
            description: The description of the visit
            location: A dictionary containing location information
            start_time: The start time
            end_time: The end time
            booking_required: Whether booking is required
            booking_id: The booking ID (optional)
            
        Returns:
            The visit event
        """
        event = {
            "event_type": "visit",
            "description": description,
            "location": location,
            "start_time": start_time,
            "end_time": end_time,
            "booking_required": booking_required
        }
        
        # Add booking ID if provided
        if booking_id:
            event["booking_id"] = booking_id
        
        # Add the event to the itinerary
        self._add_event_to_day(session_id, day_number, event)
        
        return event
    
    def add_hotel(self, session_id: str,
                day_number: int,
                hotel_name: str,
                address: str,
                check_in_time: str,
                check_out_time: str,
                room_selection: str = "",
                price: str = "",
                booking_id: str = "") -> Dict[str, Any]:
        """
        Add a hotel event to the itinerary.
        
        Args:
            session_id: The session identifier
            day_number: The day number
            hotel_name: The name of the hotel
            address: The address of the hotel
            check_in_time: The check-in time
            check_out_time: The check-out time
            room_selection: The room selection (optional)
            price: The price (optional)
            booking_id: The booking ID (optional)
            
        Returns:
            The hotel event
        """
        event = {
            "event_type": "hotel",
            "description": f"Check into {hotel_name}",
            "address": address,
            "check_in_time": check_in_time,
            "check_out_time": check_out_time,
            "booking_required": True
        }
        
        # Add optional fields if provided
        if room_selection:
            event["room_selection"] = room_selection
        if price:
            event["price"] = price
        if booking_id:
            event["booking_id"] = booking_id
        
        # Add the event to the itinerary
        self._add_event_to_day(session_id, day_number, event)
        
        return event
    
    def _add_event_to_day(self, session_id: str, day_number: int, event: Dict[str, Any]) -> None:
        """
        Add an event to a specific day in the itinerary.
        
        Args:
            session_id: The session identifier
            day_number: The day number
            event: The event to add
        """
        itinerary = self.get_itinerary(session_id)
        
        # Check if the itinerary exists
        if not itinerary or "days" not in itinerary:
            return
        
        # Find the day with the specified day_number
        for day in itinerary["days"]:
            if day.get("day_number") == day_number:
                if "events" not in day:
                    day["events"] = []
                day["events"].append(event)
                break
        
        # Update the itinerary in the state
        state_manager.update_state(session_id, "itinerary", itinerary)
    
    def get_day_events(self, session_id: str, day_number: int) -> List[Dict[str, Any]]:
        """
        Get the events for a specific day in the itinerary.
        
        Args:
            session_id: The session identifier
            day_number: The day number
            
        Returns:
            List of events for the specified day
        """
        itinerary = self.get_itinerary(session_id)
        
        # Check if the itinerary exists
        if not itinerary or "days" not in itinerary:
            return []
        
        # Find the day with the specified day_number
        for day in itinerary["days"]:
            if day.get("day_number") == day_number:
                return day.get("events", [])
        
        return []
    
    def get_current_day(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current day based on the itinerary_datetime value.
        
        Args:
            session_id: The session identifier
            
        Returns:
            The current day or None if not found
        """
        itinerary = self.get_itinerary(session_id)
        
        # Check if the itinerary exists
        if not itinerary or "days" not in itinerary:
            return None
        
        # Get the itinerary_datetime value
        itinerary_datetime = state_manager.get_state(session_id).get("itinerary_datetime", "")
        
        # If no itinerary_datetime, return the first day
        if not itinerary_datetime:
            return itinerary["days"][0] if itinerary["days"] else None
        
        # Extract the date part of the datetime
        try:
            current_date = datetime.fromisoformat(itinerary_datetime.replace(" ", "T")).date().isoformat()
        except (ValueError, TypeError):
            return itinerary["days"][0] if itinerary["days"] else None
        
        # Find the day with the matching date
        for day in itinerary["days"]:
            if day.get("date") == current_date:
                return day
        
        # If no matching day, return the first day
        return itinerary["days"][0] if itinerary["days"] else None

# Create a singleton instance
itinerary_manager = ItineraryManager()
