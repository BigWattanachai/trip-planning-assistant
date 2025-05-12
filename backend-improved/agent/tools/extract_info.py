"""
Tools for extracting travel information from user queries.
"""
import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def extract_travel_info(query: str) -> Dict[str, Any]:
    """
    Extract travel information from the user query.
    
    Args:
        query: The user query
        
    Returns:
        Dictionary with extracted travel info
    """
    # Initialize default values
    travel_info = {
        "origin": "กรุงเทพ",  # Default origin
        "destination": "ภายในประเทศไทย",  # Default destination
        "start_date": "ไม่ระบุ",
        "end_date": "ไม่ระบุ",
        "budget": "ไม่ระบุ",
        "num_travelers": 1,
        "preferences": []
    }
    
    # Extract origin
    origin_match = re.search(r"ต้นทาง:\s*([^\n]+)", query)
    if origin_match:
        travel_info["origin"] = origin_match.group(1).strip()
    
    # Extract destination
    destination_match = re.search(r"ปลายทาง:\s*([^\n]+)", query)
    if destination_match:
        travel_info["destination"] = destination_match.group(1).strip()
    
    # Extract dates
    dates_match = re.search(r"ช่วงเวลาเดินทาง:.*?วันที่:\s*(\d{4}-\d{2}-\d{2})(?:\s*ถึงวันที่\s*(\d{4}-\d{2}-\d{2}))?", query)
    if dates_match:
        travel_info["start_date"] = dates_match.group(1).strip()
        if dates_match.group(2):
            travel_info["end_date"] = dates_match.group(2).strip()
        else:
            travel_info["end_date"] = travel_info["start_date"]  # Same day trip
    
    # Extract budget
    budget_match = re.search(r"งบประมาณรวม:\s*ไม่เกิน\s*(\d+,?\d*)\s*บาท", query)
    if budget_match:
        travel_info["budget"] = budget_match.group(1).strip()
    
    # Extract number of travelers
    travelers_match = re.search(r"จำนวนผู้เดินทาง:\s*(\d+)", query)
    if travelers_match:
        travel_info["num_travelers"] = int(travelers_match.group(1).strip())
    
    # Extract preferences
    preferences_match = re.search(r"ความต้องการพิเศษ:\s*(.+?)(?:\n|$)", query, re.DOTALL)
    if preferences_match:
        preferences_text = preferences_match.group(1).strip()
        # Split by commas or bullet points
        preferences = re.split(r'[,•]', preferences_text)
        travel_info["preferences"] = [p.strip() for p in preferences if p.strip()]
    
    # Check for implicit travel information
    # If destination is not specified but mentioned in the query
    if travel_info["destination"] == "ภายในประเทศไทย":
        # Look for city or province names in the query
        thai_destinations = [
            "กรุงเทพ", "เชียงใหม่", "เชียงราย", "ภูเก็ต", "พัทยา", "หัวหิน", 
            "กระบี่", "พังงา", "เกาะสมุย", "เกาะพีพี", "เกาะเต่า", "เกาะช้าง",
            "อยุธยา", "สุโขทัย", "ลพบุรี", "นครราชสีมา", "ขอนแก่น", "อุดรธานี",
            "ระยอง", "จันทบุรี", "ตราด", "ประจวบคีรีขันธ์", "ชุมพร", "สุราษฎร์ธานี",
            "นครศรีธรรมราช", "สงขลา", "ตรัง", "สตูล", "พัทลุง", "ชลบุรี",
            "แม่ฮ่องสอน", "น่าน", "พะเยา", "ลำปาง", "ลำพูน", "แพร่", "อุตรดิตถ์",
            "ตาก", "กำแพงเพชร", "พิษณุโลก", "พิจิตร", "เพชรบูรณ์", "นครสวรรค์"
        ]
        
        for destination in thai_destinations:
            if destination in query:
                travel_info["destination"] = destination
                break
    
    # If dates are not specified but mentioned in the query
    if travel_info["start_date"] == "ไม่ระบุ":
        # Look for date patterns in the query (YYYY-MM-DD format)
        date_matches = re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", query)
        if len(date_matches) >= 1:
            travel_info["start_date"] = date_matches[0]
            if len(date_matches) >= 2:
                travel_info["end_date"] = date_matches[1]
            else:
                travel_info["end_date"] = date_matches[0]
    
    # If budget is not specified but mentioned in the query
    if travel_info["budget"] == "ไม่ระบุ":
        # Look for budget patterns in the query
        budget_matches = re.findall(r"(\d+[,\d]*)\s*บาท", query)
        if budget_matches:
            # Use the highest value as the budget
            budgets = [int(b.replace(",", "")) for b in budget_matches]
            travel_info["budget"] = f"{max(budgets):,}"
    
    logger.info(f"Extracted travel info: {travel_info}")
    return travel_info

def classify_query(query: str) -> str:
    """
    Classify the query type to determine which sub-agent to use.
    
    Args:
        query: The user query
        
    Returns:
        String indicating the query type: "accommodation", "activity", 
        "restaurant", "transportation", "travel_planner", or "general"
    """
    query_lower = query.lower()
    
    # Check if this is a travel planning request
    if "ช่วยวางแผนการเดินทางท่องเที่ยว" in query_lower:
        return "travel_planner"
    
    # Check for accommodation-related queries
    if any(keyword in query_lower for keyword in ["ที่พัก", "โรงแรม", "รีสอร์ท", "โฮสเทล", "พักที่ไหนดี"]):
        return "accommodation"
    
    # Check for activity-related queries
    if any(keyword in query_lower for keyword in ["สถานที่ท่องเที่ยว", "กิจกรรม", "เที่ยวที่ไหนดี", "สถานที่น่าสนใจ"]):
        return "activity"
    
    # Check for restaurant-related queries
    if any(keyword in query_lower for keyword in ["ร้านอาหาร", "กินที่ไหนดี", "อาหาร", "ร้านอร่อย"]):
        return "restaurant"
    
    # Check for transportation-related queries
    if any(keyword in query_lower for keyword in ["การเดินทาง", "เดินทางยังไง", "รถ", "เครื่องบิน", "รถไฟ", "รถทัวร์"]):
        return "transportation"
    
    # Default to general if no specific category is detected
    return "general"
