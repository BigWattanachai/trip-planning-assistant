import os
from typing import Dict, List, Any
from datetime import datetime, timedelta
from google.adk import LlmAgent
from google.adk.tools import function_tool, search_tool
import aiohttp
import json

class FlightSearchAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="FlightSearchAgent",
            model="gemini-1.5-flash",
            system_prompt="""คุณเป็นผู้เชี่ยวชาญด้านการจองตั๋วเครื่องบินและการเดินทางทางอากาศ 
            มีหน้าที่ค้นหาและแนะนำเที่ยวบินที่เหมาะสมกับความต้องการของผู้ใช้
            
            คุณต้อง:
            1. ค้นหาเที่ยวบินที่ตรงกับวันเดินทางและงบประมาณ
            2. เปรียบเทียบตัวเลือกจากสายการบินต่างๆ
            3. พิจารณาเวลาเดินทาง, จำนวนจุดแวะพัก, และความสะดวกสบาย
            4. แนะนำเที่ยวบินทั้งขาไปและขากลับ
            5. ให้ข้อมูลสัมภาระ, บริการบนเครื่อง, และข้อควรระวัง
            6. แนะนำเวลาที่เหมาะสมในการจองเพื่อราคาที่ดี"""
        )
        
        # Add search tool
        self.add_tool(search_tool(
            search_engine="google",
            max_results=10
        ))
        
        # Add custom flight search tool
        self.add_tool(self._create_flight_search_tool())
    
    def _create_flight_search_tool(self):
        @function_tool
        async def search_flights(
            origin: str,
            destination: str,
            departure_date: str,
            return_date: str = None,
            cabin_class: str = "economy",
            max_price: float = None
        ) -> Dict:
            """Search for flights between origin and destination"""
            # Parse dates
            dep_date = datetime.strptime(departure_date, "%Y-%m-%d")
            ret_date = datetime.strptime(return_date, "%Y-%m-%d") if return_date else None
            
            # Simulated flight data - in production, use actual flight APIs
            flights = {
                "outbound_flights": [
                    {
                        "id": "1",
                        "airline": "Thai Airways",
                        "flightNumber": "TG123",
                        "departure": {
                            "airport": f"{origin} International Airport",
                            "code": origin[:3].upper(),
                            "time": f"{dep_date.strftime('%Y-%m-%d')}T08:00:00",
                            "terminal": "1"
                        },
                        "arrival": {
                            "airport": f"{destination} International Airport",
                            "code": destination[:3].upper(),
                            "time": f"{dep_date.strftime('%Y-%m-%d')}T14:00:00",
                            "terminal": "2"
                        },
                        "duration": "6h 00m",
                        "stops": 0,
                        "price": 650,
                        "currency": "USD",
                        "class": cabin_class.title(),
                        "aircraft": "Boeing 787-9",
                        "baggage": {
                            "cabin": "7kg",
                            "checked": "30kg"
                        },
                        "amenities": [
                            "In-flight entertainment",
                            "Meals included",
                            "Power outlets",
                            "WiFi available"
                        ],
                        "bookingUrl": f"https://thaiairways.com/book?flight=TG123"
                    },
                    {
                        "id": "2",
                        "airline": "Singapore Airlines",
                        "flightNumber": "SQ456",
                        "departure": {
                            "airport": f"{origin} International Airport",
                            "code": origin[:3].upper(),
                            "time": f"{dep_date.strftime('%Y-%m-%d')}T10:30:00",
                            "terminal": "2"
                        },
                        "arrival": {
                            "airport": f"{destination} International Airport",
                            "code": destination[:3].upper(),
                            "time": f"{dep_date.strftime('%Y-%m-%d')}T16:45:00",
                            "terminal": "3"
                        },
                        "duration": "6h 15m",
                        "stops": 0,
                        "price": 720,
                        "currency": "USD",
                        "class": cabin_class.title(),
                        "aircraft": "Airbus A350-900",
                        "baggage": {
                            "cabin": "7kg",
                            "checked": "30kg"
                        },
                        "amenities": [
                            "Premium entertainment",
                            "Gourmet meals",
                            "Power outlets",
                            "WiFi available"
                        ],
                        "bookingUrl": f"https://singaporeair.com/book?flight=SQ456"
                    },
                    {
                        "id": "3",
                        "airline": "Emirates",
                        "flightNumber": "EK789",
                        "departure": {
                            "airport": f"{origin} International Airport",
                            "code": origin[:3].upper(),
                            "time": f"{dep_date.strftime('%Y-%m-%d')}T22:00:00",
                            "terminal": "3"
                        },
                        "arrival": {
                            "airport": f"{destination} International Airport",
                            "code": destination[:3].upper(),
                            "time": f"{(dep_date + timedelta(days=1)).strftime('%Y-%m-%d')}T09:30:00",
                            "terminal": "1"
                        },
                        "duration": "11h 30m",
                        "stops": 1,
                        "price": 580,
                        "currency": "USD",
                        "class": cabin_class.title(),
                        "aircraft": "Boeing 777-300ER",
                        "baggage": {
                            "cabin": "7kg",
                            "checked": "35kg"
                        },
                        "amenities": [
                            "ICE entertainment",
                            "Multi-course meals",
                            "Power outlets",
                            "WiFi available"
                        ],
                        "stopover": {
                            "airport": "Dubai International Airport",
                            "duration": "2h 30m"
                        },
                        "bookingUrl": f"https://emirates.com/book?flight=EK789"
                    }
                ],
                "return_flights": [] if not return_date else [
                    {
                        "id": "4",
                        "airline": "Thai Airways",
                        "flightNumber": "TG124",
                        "departure": {
                            "airport": f"{destination} International Airport",
                            "code": destination[:3].upper(),
                            "time": f"{ret_date.strftime('%Y-%m-%d')}T16:00:00",
                            "terminal": "2"
                        },
                        "arrival": {
                            "airport": f"{origin} International Airport",
                            "code": origin[:3].upper(),
                            "time": f"{ret_date.strftime('%Y-%m-%d')}T22:00:00",
                            "terminal": "1"
                        },
                        "duration": "6h 00m",
                        "stops": 0,
                        "price": 650,
                        "currency": "USD",
                        "class": cabin_class.title(),
                        "aircraft": "Boeing 787-9",
                        "baggage": {
                            "cabin": "7kg",
                            "checked": "30kg"
                        },
                        "amenities": [
                            "In-flight entertainment",
                            "Meals included",
                            "Power outlets",
                            "WiFi available"
                        ],
                        "bookingUrl": f"https://thaiairways.com/book?flight=TG124"
                    }
                ]
            }
            
            return flights
        
        return search_flights
    
    async def run_async(self, context: Dict) -> Dict:
        """Search for flights based on trip context"""
        departure = context.get("departure")
        destination = context.get("destination")
        start_date = context.get("start_date")
        end_date = context.get("end_date")
        budget = context.get("budget", "medium")
        preferences = context.get("preferences", {})
        
        # Map budget to cabin class
        cabin_map = {
            "budget": "economy",
            "medium": "economy",
            "luxury": "business"
        }
        cabin_class = cabin_map.get(budget, "economy")
        
        # Search for flights using our custom tool
        flight_results = await self.use_tool(
            "search_flights",
            origin=departure,
            destination=destination,
            departure_date=start_date,
            return_date=end_date,
            cabin_class=cabin_class
        )
        
        # Use search tool for additional flight information
        search_query = f"flights from {departure} to {destination} {start_date} airlines review tips"
        web_results = await self.use_tool("search_tool", query=search_query)
        
        # Generate recommendations using LLM
        query = f"""
        Based on the following flight options, recommend the best flights for this trip:
        
        Trip Details:
        - From: {departure} to {destination}
        - Dates: {start_date} to {end_date}
        - Budget: {budget}
        - Cabin Class: {cabin_class}
        
        Available Flights:
        Outbound: {json.dumps(flight_results['outbound_flights'], indent=2)}
        Return: {json.dumps(flight_results['return_flights'], indent=2)}
        
        Additional Information:
        {web_results}
        
        Please provide:
        1. Recommended flight combination (outbound + return)
        2. Pros and cons of each option
        3. Best value for money analysis
        4. Tips for booking and check-in
        5. Airport transfer recommendations
        6. Airline service quality comparison
        
        Consider factors like:
        - Total travel time
        - Number of stops
        - Departure/arrival times
        - Airline reputation
        - Price
        - Baggage allowance
        
        Format the response to help travelers make an informed decision.
        """
        
        response = await self.generate_async(query)
        
        # Combine outbound and return flights for display
        all_flights = []
        
        for flight in flight_results.get('outbound_flights', []):
            flight['direction'] = 'outbound'
            all_flights.append(flight)
        
        for flight in flight_results.get('return_flights', []):
            flight['direction'] = 'return'
            all_flights.append(flight)
        
        return {
            "flights": all_flights,
            "recommendations": response,
            "booking_tips": {
                "best_booking_time": "Book 6-8 weeks in advance for best prices",
                "flexibility_tip": "Consider flexible dates for better deals",
                "loyalty_programs": "Join airline loyalty programs for benefits"
            },
            "airport_info": {
                departure: {
                    "transport_options": ["Taxi", "Airport Express", "Public Bus"],
                    "recommended_arrival": "2 hours before for domestic, 3 hours for international"
                },
                destination: {
                    "transport_options": ["Airport Rail Link", "Taxi", "Hotel Shuttle"],
                    "currency_exchange": "Available at airport, but better rates in city"
                }
            }
        }
