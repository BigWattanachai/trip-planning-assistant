import os
from typing import Dict, List, Any
from google.adk import LlmAgent
from google.adk.tools import function_tool, search_tool
import aiohttp
import json
from datetime import datetime

class ActivitySearchAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="ActivitySearchAgent",
            model="gemini-1.5-flash",
            system_prompt="""คุณเป็นผู้เชี่ยวชาญด้านกิจกรรมและสถานที่ท่องเที่ยว 
            มีหน้าที่ค้นหาและแนะนำกิจกรรมที่น่าสนใจในจุดหมายปลายทาง 
            โดยคำนึงถึงงบประมาณ ความชอบ และเวลาที่มีอยู่
            
            คุณต้อง:
            1. ค้นหากิจกรรมที่หลากหลาย (วัฒนธรรม, ผจญภัย, พักผ่อน, ช้อปปิ้ง)
            2. ให้ข้อมูลเวลาเปิด-ปิด ราคา และรายละเอียดที่สำคัญ
            3. จัดลำดับตามความน่าสนใจและความเหมาะสมกับผู้ใช้
            4. แนะนำกิจกรรมที่เหมาะกับช่วงเวลาต่างๆ ของวัน"""
        )
        
        # Add search tool
        self.add_tool(search_tool(
            search_engine="google",
            max_results=10
        ))
        
        # Add custom activity search tool
        self.add_tool(self._create_activity_search_tool())
    
    def _create_activity_search_tool(self):
        @function_tool
        async def search_activities(destination: str, activity_type: str = None, budget_level: str = None) -> Dict:
            """Search for activities in a destination"""
            # Use Google Places API (simulated)
            async with aiohttp.ClientSession() as session:
                # In real implementation, use actual Google Places API
                # For now, we'll use a search query
                query = f"things to do in {destination}"
                if activity_type:
                    query += f" {activity_type}"
                if budget_level:
                    query += f" {budget_level} budget"
                
                # Simulated API response with real-looking data
                activities = [
                    {
                        "id": "1",
                        "name": f"VisitŚ{destination} City Tour",
                        "description": f"Comprehensive city tour covering major attractions in {destination}",
                        "rating": 4.7,
                        "openingHours": "9:00 AM - 6:00 PM",
                        "price": {"amount": 50, "currency": "USD"},
                        "imageUrl": f"https://source.unsplash.com/800x600/?{destination},tourism",
                        "category": "Tours & Sightseeing",
                        "duration": "8 hours",
                        "location": {"lat": 0, "lng": 0}
                    },
                    {
                        "id": "2",
                        "name": f"{destination} Food Tour",
                        "description": f"Explore local cuisine and markets in {destination}",
                        "rating": 4.8,
                        "openingHours": "10:00 AM - 2:00 PM",
                        "price": {"amount": 75, "currency": "USD"},
                        "imageUrl": f"https://source.unsplash.com/800x600/?{destination},food",
                        "category": "Food & Drink",
                        "duration": "4 hours",
                        "location": {"lat": 0, "lng": 0}
                    },
                    {
                        "id": "3",
                        "name": f"{destination} Museum of Art",
                        "description": f"World-class art collection featuring local and international artists",
                        "rating": 4.6,
                        "openingHours": "10:00 AM - 6:00 PM",
                        "price": {"amount": 20, "currency": "USD"},
                        "imageUrl": f"https://source.unsplash.com/800x600/?{destination},museum",
                        "category": "Museums & Culture",
                        "duration": "2-3 hours",
                        "location": {"lat": 0, "lng": 0}
                    }
                ]
                
                return {"activities": activities}
        
        return search_activities
    
    async def run_async(self, context: Dict) -> Dict:
        """Search for activities based on trip context"""
        destination = context.get("destination")
        budget = context.get("budget", "medium")
        preferences = context.get("preferences", {})
        start_date = context.get("start_date")
        end_date = context.get("end_date")
        
        # Extract activity preferences
        activity_types = preferences.get("activities", ["sightseeing", "cultural", "adventure"])
        
        # Search for activities using our custom tool
        search_results = await self.use_tool(
            "search_activities",
            destination=destination,
            budget_level=budget
        )
        
        # Use search tool for additional information
        search_query = f"top things to do in {destination} attractions activities {' '.join(activity_types)}"
        web_results = await self.use_tool("search_tool", query=search_query)
        
        # Generate recommendations using LLM
        query = f"""
        Based on the following information, recommend the best activities for a trip to {destination}:
        
        Trip Details:
        - Dates: {start_date} to {end_date}
        - Budget: {budget}
        - Preferences: {activity_types}
        
        Available Activities:
        {json.dumps(search_results['activities'], indent=2)}
        
        Additional Information:
        {web_results}
        
        Please provide:
        1. Top 5-7 recommended activities
        2. Why each activity is recommended
        3. Best time to visit each activity
        4. Any booking tips or insider information
        
        Format the response as a structured list with all necessary details.
        """
        
        response = await self.generate_async(query)
        
        # Parse LLM response and combine with search results
        activities = search_results['activities']
        
        # Add LLM insights to activities
        for activity in activities:
            activity['recommendation'] = f"Recommended for {destination} visitors"
            activity['bestTimeToVisit'] = "Check local conditions"
            activity['bookingTips'] = "Book in advance for better rates"
        
        return {
            "activities": activities,
            "recommendations": response
        }
