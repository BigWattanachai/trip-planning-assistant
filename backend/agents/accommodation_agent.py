import os
from typing import Dict, List, Any
from google.adk import LlmAgent
from google.adk.tools import function_tool, search_tool
import aiohttp
import json
from datetime import datetime

class AccommodationAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="AccommodationAgent",
            model="gemini-1.5-flash",
            system_prompt="""คุณเป็นผู้เชี่ยวชาญด้านที่พักและโรงแรม 
            มีหน้าที่ค้นหาและแนะนำที่พักที่เหมาะสมกับความต้องการของผู้ใช้
            
            คุณต้อง:
            1. ค้นหาที่พักจากหลายแพลตฟอร์ม (Airbnb, Agoda, TripAdvisor)
            2. พิจารณาทำเล, ราคา, สิ่งอำนวยความสะดวก, และรีวิว
            3. แนะนำที่พักหลากหลายประเภท (โรงแรม, บูทีค, โฮสเทล, อพาร์ทเมนท์)
            4. ให้ข้อมูลการเดินทางจากที่พักไปยังสถานที่สำคัญ
            5. แนะนำย่านที่เหมาะสมสำหรับการพักตามสไตล์การเดินทาง
            6. ระบุนโยบายการยกเลิกและข้อควรรู้"""
        )
        
        # Add search tool
        self.add_tool(search_tool(
            search_engine="google",
            max_results=10
        ))
        
        # Add custom accommodation search tool
        self.add_tool(self._create_accommodation_search_tool())
    
    def _create_accommodation_search_tool(self):
        @function_tool
        async def search_accommodations(
            destination: str,
            check_in: str,
            check_out: str,
            budget_level: str = "medium",
            accommodation_type: str = None,
            guests: int = 2
        ) -> Dict:
            """Search for accommodations in a destination"""
            # Map budget to price ranges
            price_ranges = {
                "budget": (20, 80),
                "medium": (80, 200),
                "luxury": (200, 1000)
            }
            min_price, max_price = price_ranges.get(budget_level, (80, 200))
            
            # Simulated accommodation data
            accommodations = [
                {
                    "id": "1",
                    "name": f"{destination} Grand Hotel",
                    "type": "Luxury Hotel",
                    "rating": 4.8,
                    "reviewCount": 1250,
                    "price": 250,
                    "priceUnit": "night",
                    "amenities": [
                        "WiFi",
                        "Pool",
                        "Fitness Center",
                        "Spa",
                        "Restaurant",
                        "Business Center",
                        "Concierge",
                        "Room Service"
                    ],
                    "imageUrl": f"https://source.unsplash.com/800x600/?luxury-hotel,{destination}",
                    "platform": "Agoda",
                    "bookingUrl": "https://agoda.com/example",
                    "address": f"123 Luxury Lane, Central {destination}",
                    "location": {
                        "lat": 0,
                        "lng": 0,
                        "neighborhood": "City Center",
                        "distanceToCenter": "0.5 km"
                    },
                    "roomTypes": [
                        {
                            "name": "Deluxe Room",
                            "size": "35 sqm",
                            "bedType": "King",
                            "maxOccupancy": 2,
                            "price": 250
                        },
                        {
                            "name": "Executive Suite",
                            "size": "55 sqm",
                            "bedType": "King",
                            "maxOccupancy": 3,
                            "price": 400
                        }
                    ],
                    "policies": {
                        "checkIn": "3:00 PM",
                        "checkOut": "12:00 PM",
                        "cancellation": "Free cancellation up to 24 hours before check-in"
                    },
                    "highlights": [
                        "Rooftop bar with city views",
                        "Award-winning restaurant",
                        "Luxury spa treatments"
                    ]
                },
                {
                    "id": "2",
                    "name": f"Boutique Stay {destination}",
                    "type": "Boutique Hotel",
                    "rating": 4.6,
                    "reviewCount": 450,
                    "price": 120,
                    "priceUnit": "night",
                    "amenities": [
                        "WiFi",
                        "Breakfast",
                        "Terrace",
                        "Bar",
                        "Pet Friendly",
                        "Bicycle Rental"
                    ],
                    "imageUrl": f"https://source.unsplash.com/800x600/?boutique-hotel,{destination}",
                    "platform": "TripAdvisor",
                    "bookingUrl": "https://tripadvisor.com/example",
                    "address": f"45 Heritage Street, Old Town {destination}",
                    "location": {
                        "lat": 0,
                        "lng": 0,
                        "neighborhood": "Old Town",
                        "distanceToCenter": "1.2 km"
                    },
                    "roomTypes": [
                        {
                            "name": "Standard Room",
                            "size": "25 sqm",
                            "bedType": "Queen",
                            "maxOccupancy": 2,
                            "price": 120
                        }
                    ],
                    "policies": {
                        "checkIn": "2:00 PM",
                        "checkOut": "11:00 AM",
                        "cancellation": "Free cancellation up to 48 hours before check-in"
                    },
                    "highlights": [
                        "Charming historic building",
                        "Local art gallery",
                        "Organic breakfast"
                    ]
                },
                {
                    "id": "3",
                    "name": f"{destination} City Apartment",
                    "type": "Apartment",
                    "rating": 4.7,
                    "reviewCount": 89,
                    "price": 85,
                    "priceUnit": "night",
                    "amenities": [
                        "WiFi",
                        "Kitchen",
                        "Washing Machine",
                        "Air Conditioning",
                        "TV",
                        "Private Entrance"
                    ],
                    "imageUrl": f"https://source.unsplash.com/800x600/?apartment,{destination}",
                    "platform": "Airbnb",
                    "bookingUrl": "https://airbnb.com/example",
                    "address": f"78 Modern Avenue, {destination}",
                    "location": {
                        "lat": 0,
                        "lng": 0,
                        "neighborhood": "Shopping District",
                        "distanceToCenter": "0.8 km"
                    },
                    "roomTypes": [
                        {
                            "name": "1 Bedroom Apartment",
                            "size": "45 sqm",
                            "bedType": "Queen",
                            "maxOccupancy": 2,
                            "price": 85
                        }
                    ],
                    "policies": {
                        "checkIn": "4:00 PM - 10:00 PM",
                        "checkOut": "11:00 AM",
                        "cancellation": "Moderate - Free cancellation up to 5 days before check-in"
                    },
                    "highlights": [
                        "Self check-in",
                        "Fully equipped kitchen",
                        "Great for longer stays"
                    ]
                }
            ]
            
            # Filter by price range
            filtered_accommodations = [
                acc for acc in accommodations 
                if min_price <= acc['price'] <= max_price
            ]
            
            return {"accommodations": filtered_accommodations}
        
        return search_accommodations
    
    async def run_async(self, context: Dict) -> Dict:
        """Search for accommodations based on trip context"""
        destination = context.get("destination")
        start_date = context.get("start_date")
        end_date = context.get("end_date")
        budget = context.get("budget", "medium")
        preferences = context.get("preferences", {})
        
        # Extract accommodation preferences
        accommodation_type = preferences.get("accommodation_type", "any")
        guests = preferences.get("guests", 2)
        
        # Search for accommodations using our custom tool
        accommodation_results = await self.use_tool(
            "search_accommodations",
            destination=destination,
            check_in=start_date,
            check_out=end_date,
            budget_level=budget,
            accommodation_type=accommodation_type,
            guests=guests
        )
        
        # Use search tool for additional information
        search_query = f"best places to stay in {destination} hotels neighborhoods {budget} accommodation"
        web_results = await self.use_tool("search_tool", query=search_query)
        
        # Generate recommendations using LLM
        query = f"""
        Based on the following accommodation options, recommend the best places to stay in {destination}:
        
        Trip Details:
        - Dates: {start_date} to {end_date}
        - Budget: {budget}
        - Guests: {guests}
        - Preferences: {preferences}
        
        Available Accommodations:
        {json.dumps(accommodation_results['accommodations'], indent=2)}
        
        Additional Information:
        {web_results}
        
        Please provide:
        1. Top 3-5 recommended accommodations
        2. Why each accommodation is recommended
        3. Best neighborhoods to stay in
        4. Pros and cons of each option
        5. Transportation tips from each location
        6. Booking advice and best platforms
        7. Alternative options if fully booked
        
        Consider factors like:
        - Location convenience
        - Value for money
        - Guest reviews
        - Amenities
        - Safety
        - Local experience
        
        Also provide neighborhood guide:
        - Best areas for tourists
        - Areas to avoid
        - Local tips for each neighborhood
        
        Format the response to help travelers choose the perfect accommodation.
        """
        
        response = await self.generate_async(query)
        
        # Process and enhance accommodation data
        accommodations = accommodation_results['accommodations']
        
        # Add additional context based on LLM insights
        for acc in accommodations:
            acc['locationScore'] = self._calculate_location_score(acc['location'])
            acc['valueScore'] = self._calculate_value_score(acc['price'], acc['rating'], acc['amenities'])
            acc['recommendation'] = f"Recommended for {budget} budget travelers"
        
        return {
            "accommodations": accommodations,
            "recommendations": response,
            "neighborhood_guide": {
                "best_areas": [
                    {
                        "name": "City Center",
                        "description": "Convenient for sightseeing and shopping",
                        "pros": ["Walking distance to attractions", "Many restaurants"],
                        "cons": ["Can be noisy", "Higher prices"]
                    },
                    {
                        "name": "Old Town",
                        "description": "Cultural heart with historic charm",
                        "pros": ["Authentic atmosphere", "Local markets"],
                        "cons": ["Limited modern amenities", "Narrow streets"]
                    },
                    {
                        "name": "Business District",
                        "description": "Modern area with high-rise hotels",
                        "pros": ["Modern facilities", "Good transport links"],
                        "cons": ["Less character", "Far from historic sites"]
                    }
                ],
                "transportation_tips": {
                    "from_airport": "Airport rail link to city center, then taxi or metro",
                    "getting_around": "Use public transport pass for best value",
                    "to_attractions": "Most attractions accessible by metro or bus"
                }
            },
            "booking_tips": {
                "best_time": "Book 2-3 months in advance for best rates",
                "platforms": {
                    "Agoda": "Good for Asian destinations",
                    "Booking.com": "Wide selection, flexible cancellation",
                    "Airbnb": "Best for apartments and unique stays"
                },
                "insider_tips": [
                    "Check reviews from recent guests",
                    "Compare prices across platforms",
                    "Look for free cancellation options"
                ]
            }
        }
    
    def _calculate_location_score(self, location: Dict) -> float:
        """Calculate location score based on distance to center"""
        distance_str = location.get('distanceToCenter', '5 km')
        distance = float(distance_str.split()[0])
        
        if distance < 1:
            return 5.0
        elif distance < 2:
            return 4.5
        elif distance < 3:
            return 4.0
        elif distance < 5:
            return 3.5
        else:
            return 3.0
    
    def _calculate_value_score(self, price: float, rating: float, amenities: List[str]) -> float:
        """Calculate value score based on price, rating, and amenities"""
        amenity_score = len(amenities) / 10  # Score based on number of amenities
        price_factor = 1000 / price  # Inverse price factor
        
        value_score = (rating + amenity_score + price_factor) / 3
        return min(5.0, max(1.0, value_score))
