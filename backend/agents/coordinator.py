import os
from typing import Dict, Any, Optional
from google.adk import LlmAgent
from google.adk.tools import search_tool
from google.adk.sessions import Session

class TravelCoordinator(LlmAgent):
    def __init__(self):
        super().__init__(
            name="Travel Coordinator",
            model="gemini-1.5-pro",
            system_prompt="""คุณเป็นผู้ประสานงานการวางแผนการเดินทางที่เชี่ยวชาญ 
            มีหน้าที่ในการ:
            1. เข้าใจความต้องการของผู้ใช้
            2. ประสานงานกับ Agent เฉพาะทาง
            3. สังเคราะห์ข้อมูลจากแหล่งต่างๆ
            4. นำเสนอแผนการเดินทาง พร้อมรายละเอียดครบถ้วนที่สมบูรณ์
            
            คุณต้องให้คำแนะนำที่เป็นประโยชน์และเข้าใจง่าย โดยคำนึงถึงงบประมาณและความชอบของผู้ใช้เสมอ"""
        )
        
        # Add search tool for additional research
        self.add_tool(search_tool(
            search_engine="google",
            max_results=5
        ))
    
    async def run_async(self, context: Dict) -> Dict:
        """
        Coordinate the trip planning process
        """
        # Extract context information
        departure = context.get("departure")
        destination = context.get("destination")
        start_date = context.get("start_date")
        end_date = context.get("end_date")
        budget = context.get("budget")
        preferences = context.get("preferences", {})
        
        # If we receive aggregated results from other agents
        if "activities" in context:
            # Synthesize the results
            query = f"""
            สังเคราะห์ข้อมูลการเดินทางต่อไปนี้เป็นแผนการเดินทางที่สมบูรณ์:
            
            จุดหมายปลายทาง: {destination}
            วันที่: {start_date} ถึง {end_date}
            งบประมาณ: {budget}
            
            ข้อมูลที่รวบรวมได้:
            - กิจกรรม: {len(context.get('activities', []))} รายการ
            - ร้านอาหาร: {len(context.get('restaurants', []))} รายการ
            - เที่ยวบิน: {len(context.get('flights', []))} รายการ
            - ที่พัก: {len(context.get('accommodations', []))} รายการ
            - วิดีโอ: {len(context.get('videos', []))} รายการ
            
            กรุณาสร้างแผนการเดินทางที่เหมาะสมและสมดุล โดยคำนึงถึงงบประมาณและเวลา
            """
            
            response = await self.generate_async(query)
            
            # Return synthesized results
            return {
                "destination": destination,
                "departure": departure,
                "startDate": start_date,
                "endDate": end_date,
                "budget": budget,
                "activities": context.get('activities', []),
                "restaurants": context.get('restaurants', []),
                "flights": context.get('flights', []),
                "accommodations": context.get('accommodations', []),
                "videos": context.get('videos', []),
                "summary": response
            }
        else:
            # Initial planning phase - understand requirements
            query = f"""
            ผู้ใช้ต้องการวางแผนการเดินทาง:
            - จาก: {departure}
            - ไป: {destination}
            - วันที่: {start_date} ถึง {end_date}
            - งบประมาณ: {budget}
            - ความชอบ: {preferences}
            
            วิเคราะห์ความต้องการและเตรียมข้อมูลสำหรับทีมตัวแทนเฉพาะทาง
            """
            
            response = await self.generate_async(query)
            
            # Return analysis for other agents
            return {
                "departure": departure,
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "budget": budget,
                "preferences": preferences,
                "analysis": response
            }
    
    async def chat(self, message: str, session: Optional[Session] = None) -> str:
        """
        Handle chat interactions with users
        """
        context = ""
        if session and session.context:
            context = f"บริบทการสนทนา: {session.context.get_relevant_context(message)}"
        
        query = f"{context}\n\nผู้ใช้: {message}\n\nกรุณาตอบคำถามเกี่ยวกับการเดินทาง"
        
        response = await self.generate_async(query)
        
        # Update session if exists
        if session:
            session.context.add_message("user", message)
            session.context.add_message("assistant", response)
        
        return response
    
    async def research_destination(self, destination: str) -> Dict:
        """
        Research detailed information about a destination
        """
        query = f"""
        ค้นหาข้อมูลเชิงลึกเกี่ยวกับ {destination} ครอบคลุม:
        1. ข้อมูลทั่วไป
        2. สถานที่ท่องเที่ยวยอดนิยม
        3. วัฒนธรรมและประเพณี
        4. สภาพอากาศ
        5. คำแนะนำการเดินทาง
        6. ความปลอดภัย
        """
        
        # Use search tool to gather information
        search_results = await self.use_tool("search_tool", query=query)
        
        # Synthesize information
        synthesis_query = f"""
        สังเคราะห์ข้อมูลเกี่ยวกับ {destination} จากผลการค้นหา:
        {search_results}
        
        กรุณาสร้างข้อมูลที่ครอบคลุมและเป็นประโยชน์สำหรับนักท่องเที่ยว
        """
        
        response = await self.generate_async(synthesis_query)
        
        return {
            "destination": destination,
            "overview": response,
            "search_results": search_results
        }
