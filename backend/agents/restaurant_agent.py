import os
from typing import Dict, List, Any
from google.adk import LlmAgent
from google.adk.tools import function_tool, search_tool
import aiohttp
import json

class RestaurantAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="RestaurantAgent",
            model="gemini-1.5-flash",
            system_prompt="""คุณเป็นผู้เชี่ยวชาญด้านร้านอาหารและประสบการณ์การรับประทานอาหาร 
            มีหน้าที่ค้นหาและแนะนำร้านอาหารที่เหมาะกับงบประมาณและความชอบของผู้ใช้
            
            คุณต้อง:
            1. ค้นหาร้านอาหารที่หลากหลายประเภท (อาหารท้องถิ่น, นานาชาติ, ร้านดัง)
            2. พิจารณาระดับราคาให้เหมาะกับงบประมาณ
            3. ให้ข้อมูลเมนูแนะนำ, รีวิว, และบรรยากาศร้าน
            4. แนะนำร้านสำหรับมื้อต่างๆ (เช้า, กลางวัน, เย็น)
            5. ระบุข้อมูลการจองและช่วงเวลาที่แนะนำ"""
        )
        
        # Add search tool
        self.add_tool(search_tool(
            search_engine="google",
            max_results=10
        ))
        
        # Add custom restaurant search tool
        self.add_tool(self._create_restaurant_search_tool())
    
    def _create_restaurant_search_tool(self):
        @function_tool
        async def search_restaurants(destination: str, cuisine_type: str = None, price_range: str = None) -> Dict:
            """Search for restaurants in a destination"""
            # Simulated restaurant data - in production, use actual APIs
            restaurants = [
                {
                    "id": "1",
                    "name": f"{destination} Fine Dining",
                    "cuisine": "Modern European",
                    "priceRange": "$$$",
                    "rating": 4.8,
                    "reviewHighlight": "Exquisite culinary experience with innovative dishes",
                    "imageUrl": f"https://source.unsplash.com/800x600/?restaurant,fine-dining",
                    "address": f"123 Main Street, {destination}",
                    "phone": "+1 234 567 8900",
                    "website": "https://example.com",
                    "hours": {
                        "monday": "6:00 PM - 11:00 PM",
                        "tuesday": "6:00 PM - 11:00 PM",
                        "wednesday": "6:00 PM - 11:00 PM",
                        "thursday": "6:00 PM - 11:00 PM",
                        "friday": "6:00 PM - 12:00 AM",
                        "saturday": "6:00 PM - 12:00 AM",
                        "sunday": "Closed"
                    },
                    "menuHighlights": [
                        "Wagyu Beef Tenderloin",
                        "Fresh Seafood Platter",
                        "Seasonal Tasting Menu"
                    ],
                    "bookingRequired": True
                },
                {
                    "id": "2",
                    "name": f"Local Flavors of {destination}",
                    "cuisine": "Local Cuisine",
                    "priceRange": "$$",
                    "rating": 4.7,
                    "reviewHighlight": "Authentic local dishes in a traditional setting",
                    "imageUrl": f"https://source.unsplash.com/800x600/?restaurant,local-food",
                    "address": f"456 Heritage Lane, {destination}",
                    "phone": "+1 234 567 8901",
                    "hours": {
                        "monday": "11:00 AM - 10:00 PM",
                        "tuesday": "11:00 AM - 10:00 PM",
                        "wednesday": "11:00 AM - 10:00 PM",
                        "thursday": "11:00 AM - 10:00 PM",
                        "friday": "11:00 AM - 11:00 PM",
                        "saturday": "11:00 AM - 11:00 PM",
                        "sunday": "11:00 AM - 9:00 PM"
                    },
                    "menuHighlights": [
                        "Traditional Soup",
                        "Grilled Local Fish",
                        "House Special Curry"
                    ],
                    "bookingRequired": False
                },
                {
                    "id": "3",
                    "name": f"{destination} Street Food Market",
                    "cuisine": "Street Food",
                    "priceRange": "$",
                    "rating": 4.5,
                    "reviewHighlight": "Vibrant street food scene with diverse options",
                    "imageUrl": f"https://source.unsplash.com/800x600/?street-food,market",
                    "address": f"Night Market, {destination}",
                    "hours": {
                        "monday": "5:00 PM - 11:00 PM",
                        "tuesday": "5:00 PM - 11:00 PM",
                        "wednesday": "5:00 PM - 11:00 PM",
                        "thursday": "5:00 PM - 11:00 PM",
                        "friday": "5:00 PM - 12:00 AM",
                        "saturday": "5:00 PM - 12:00 AM",
                        "sunday": "5:00 PM - 11:00 PM"
                    },
                    "menuHighlights": [
                        "Fresh Spring Rolls",
                        "Grilled Skewers",
                        "Local Desserts"
                    ],
                    "bookingRequired": False
                }
            ]
            
            return {"restaurants": restaurants}
        
        return search_restaurants
    
    async def run_async(self, context: Dict) -> Dict:
        """Search for restaurants based on trip context"""
        destination = context.get("destination")
        budget = context.get("budget", "medium")
        preferences = context.get("preferences", {})
        
        # Extract food preferences
        cuisine_types = preferences.get("cuisine", ["local", "international"])
        dietary_restrictions = preferences.get("dietary", [])
        
        # Map budget to price range
        price_map = {
            "budget": "$",
            "medium": "$$",
            "luxury": "$$$"
        }
        price_range = price_map.get(budget, "$$")
        
        # Search for restaurants using our custom tool
        search_results = await self.use_tool(
            "search_restaurants",
            destination=destination,
            price_range=price_range
        )
        
        # Use search tool for additional information
        search_query = f"best restaurants in {destination} {' '.join(cuisine_types)} food dining {price_range}"
        web_results = await self.use_tool("search_tool", query=search_query)
        
        # Generate recommendations using LLM
        query = f"""
        Based on the following information, recommend the best restaurants for a trip to {destination}:
        
        Trip Details:
        - Budget: {budget} (Price range: {price_range})
        - Cuisine preferences: {cuisine_types}
        - Dietary restrictions: {dietary_restrictions}
        
        Available Restaurants:
        {json.dumps(search_results['restaurants'], indent=2)}
        
        Additional Information:
        {web_results}
        
        Please provide:
        1. Top 5-7 recommended restaurants
        2. Why each restaurant is recommended
        3. Must-try dishes at each restaurant
        4. Best time to visit (lunch/dinner)
        5. Reservation recommendations
        6. Any local dining etiquette tips
        
        Also categorize restaurants by:
        - Fine dining experiences
        - Casual local favorites
        - Street food/markets
        - Breakfast/brunch spots
        
        Format the response to be informative and helpful for travelers.
        """
        
        response = await self.generate_async(query)
        
        # Process and enhance restaurant data
        restaurants = search_results['restaurants']
        
        # Add additional context based on LLM insights
        for restaurant in restaurants:
            restaurant['recommendation'] = f"Recommended for {budget} budget travelers"
            restaurant['bestTimeToVisit'] = "Dinner" if restaurant['priceRange'] == "$$$" else "Lunch or Dinner"
            restaurant['reservationTips'] = "Reserve in advance" if restaurant.get('bookingRequired') else "Walk-ins welcome"
        
        return {
            "restaurants": restaurants,
            "recommendations": response,
            "dining_guide": {
                "local_etiquette": "Check for local customs and tipping practices",
                "peak_hours": "Lunch: 12-2 PM, Dinner: 7-9 PM",
                "budget_tips": f"Look for lunch specials and set menus for better value in {destination}"
            }
        }
