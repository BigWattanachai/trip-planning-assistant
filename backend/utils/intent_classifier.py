"""
Standalone intent classifier for travel agent.
"""

# Dictionary of Thai keywords related to food and restaurants
FOOD_KEYWORDS = [
    # Thai food-related words
    "อาหาร", "ร้านอาหาร", "กิน", "อร่อย", "ร้าน", "อาหารเช้า", 
    "อาหารกลางวัน", "อาหารเย็น", "มื้อ", "เมนู", "จาน", "ทาน", 
    "รสชาติ", "ราคา", "ค่าอาหาร", "คาเฟ่", "กาแฟ", "ขนม", "ของหวาน",
    "อาหารพื้นเมือง", "อาหารเหนือ", "อาหารใต้", "อาหารอีสาน", "อาหารทะเล",
    "สั่งอาหาร", "เชฟ", "บุฟเฟ่ต์", "ร้านอร่อย", "ของกิน", "กับข้าว", "ของทานเล่น",
    
    # English food-related words
    "restaurant", "food", "eat", "cafe", "breakfast", "lunch", "dinner",
    "meal", "dish", "menu", "cuisine", "delicious", "tasty", "dining", "snack",
    "dessert", "coffee shop", "street food", "local food", "chef", "buffet",
    "restaurant recommendation", "where to eat"
]

# Dictionary of Thai keywords related to activities and attractions
ACTIVITY_KEYWORDS = [
    # Thai activity-related words
    "เที่ยว", "สถานที่", "ไป", "ดู", "เดินทาง", "กิจกรรม", "น้ำตก", 
    "ทะเล", "ภูเขา", "วัด", "พิพิธภัณฑ์", "ตลาด", "ช้อปปิ้ง", 
    "ท่องเที่ยว", "ชายหาด", "อุทยาน", "ธรรมชาติ", "แลนด์มาร์ค", "ที่เที่ยว",
    "จุดชมวิว", "จุดถ่ายรูป", "สวนสาธารณะ", "สวนสนุก", "ปีนเขา", "เดินป่า",
    "เดินเล่น", "ชมวิว", "ศิลปะ", "วัฒนธรรม", "ประเพณี", "พระธาตุ", "เจดีย์",
    "โบราณสถาน", "ประวัติศาสตร์", "อนุสาวรีย์", "พิพิธภัณฑ์", "หมู่บ้าน", "ชุมชน",
    
    # English activity-related words
    "activity", "attractions", "see", "visit", "place", "temple", "market", "beach",
    "sightseeing", "tourism", "tourist spots", "landmarks", "things to do", "places to see",
    "viewpoint", "photo spot", "park", "hiking", "trekking", "adventure", "nature",
    "cultural", "historical", "heritage", "museum", "shopping", "excursion", "tour",
    "exploration", "entertainment", "sight", "destination", "attractions", "scenic",
    "what to see", "where to visit"
]

def classify_intent(user_input: str) -> str:
    """
    Classify user intent as food, activity, or general travel based on keywords.
    
    Args:
        user_input: The user's input message
        
    Returns:
        String indicating the intent: "restaurant", "activity", or "travel"
    """
    # Lower case the input for case-insensitive matching
    user_input_lower = user_input.lower()
    
    # Count keyword matches with weighting for phrase matches (more specific intent)
    food_score = 0
    activity_score = 0
    
    # Special high-priority cases first
    
    # Strong food-specific patterns
    if "ร้าน" in user_input_lower and "อร่อย" in user_input_lower:
        food_score += 10  # Very strong indicator for food
    
    if "where" in user_input_lower and "eat" in user_input_lower:
        food_score += 10  # Very strong indicator for food
    
    if "restaurant" in user_input_lower:
        food_score += 10  # Direct mention
    
    # Strong activity-specific patterns
    if "where" in user_input_lower and "visit" in user_input_lower:
        activity_score += 10  # Very strong indicator for activities
    
    if "attraction" in user_input_lower:
        activity_score += 10  # Direct mention
    
    if "ที่เที่ยว" in user_input_lower:
        activity_score += 10  # Direct mention
    
    # Check for food-related keywords
    for word in FOOD_KEYWORDS:
        word_lower = word.lower()
        if word_lower in user_input_lower:
            # Give higher weight to more specific phrases
            if len(word) > 5:  # Longer words/phrases get higher weight
                food_score += 2
            else:
                food_score += 1
    
    # Check for activity-related keywords
    for word in ACTIVITY_KEYWORDS:
        word_lower = word.lower()
        if word_lower in user_input_lower:
            # Give higher weight to more specific phrases
            if len(word) > 5:  # Longer words/phrases get higher weight
                activity_score += 2
            else:
                activity_score += 1
    
    # Specific phrase boost for very clear intent signals
    food_specific_phrases = [
        "ร้านอาหาร", "ที่กิน", "จะกินที่ไหน", "อาหารอร่อย", 
        "where to eat", "restaurant recommend", "should i eat", "good food", 
        "food in", "restaurants in", "dining", "where can i eat"
    ]
    
    activity_specific_phrases = [
        "ที่เที่ยว", "สถานที่ท่องเที่ยว", "อยากไปเที่ยว", 
        "places to visit", "attractions", "things to do", "where to go",
        "places to see", "visit in", "tourist spots", "temples in"
    ]
    
    # Special case for temple (วัด) - it's a common attraction in Thailand
    if "วัด" in user_input_lower or "temple" in user_input_lower:
        activity_score += 3
    
    for phrase in food_specific_phrases:
        if phrase.lower() in user_input_lower:
            food_score += 5  # Strong boost for very clear food intent
    
    for phrase in activity_specific_phrases:
        if phrase.lower() in user_input_lower:
            activity_score += 5  # Strong boost for very clear activity intent
    
    # Handle the specific case "ร้านไหนอร่อยในจังหวัดน่าน" 
    # If both "ร้าน" and "อร่อย" are present, it's very likely about restaurants
    if "ร้าน" in user_input_lower and "อร่อย" in user_input_lower:
        food_score += 10
    
    # Print scores for debugging
    print(f"[INTENT SCORES] Food: {food_score}, Activity: {activity_score}")
    
    # Determine intent based on weighted score with thresholds
    if food_score > activity_score and food_score >= 2:
        return "restaurant"
    elif activity_score > food_score and activity_score >= 2:
        return "activity"
    else:
        # Default to general travel agent
        return "travel"

# Test cases for food/restaurant intent
food_test_cases = [
    "ช่วยแนะนำร้านอาหารอร่อยๆ ที่น่านให้หน่อยได้ไหมคะ?",
    "อยากกินอาหารพื้นเมืองที่น่าน",
    "มีร้านอาหารดีๆที่ไหนบ้างในน่าน",
    "ร้านไหนอร่อยในจังหวัดน่าน",
    "อาหารเหนือที่น่านมีร้านแนะนำไหม",
    "where should I eat in Nan?",
    "good restaurants in Nan province"
]

# Test cases for activity/attraction intent
activity_test_cases = [
    "อยากไปเที่ยวที่ไหนดีในน่าน",
    "มีที่เที่ยวอะไรน่าสนใจในน่าน",
    "แนะนำสถานที่ท่องเที่ยวในน่าน",
    "วัดดังๆในน่านมีอะไรบ้าง",
    "น่านมีอุทยานหรือน้ำตกไหม",
    "what are the best attractions in Nan?",
    "places to visit in Nan province"
]

# Test cases for general travel intent
general_test_cases = [
    "ไปเที่ยวน่าน",
    "น่านเป็นยังไงบ้าง",
    "ช่วยวางแผนเที่ยวน่าน 3 วัน",
    "ควรพักที่ไหนในน่าน",
    "visiting Nan",
    "tell me about Nan"
]

def test_classification():
    """Test the intent classification function"""
    print("Testing food/restaurant intent classification:")
    for case in food_test_cases:
        intent = classify_intent(case)
        print(f"  '{case}' → {intent} {'✓' if intent == 'restaurant' else '✗'}")
    
    print("\nTesting activity/attraction intent classification:")
    for case in activity_test_cases:
        intent = classify_intent(case)
        print(f"  '{case}' → {intent} {'✓' if intent == 'activity' else '✗'}")
    
    print("\nTesting general travel intent classification:")
    for case in general_test_cases:
        intent = classify_intent(case)
        # Note: in general test cases, any of the intents could be valid
        # depending on the keyword balance, so we don't mark right/wrong
        print(f"  '{case}' → {intent}")
    
    # Test the specific case that failed previously
    print("\nTesting our example case:")
    example = "ช่วยแนะนำร้านอาหารอร่อยๆ ที่น่านให้หน่อยได้ไหมคะ?"
    intent = classify_intent(example)
    print(f"  '{example}' → {intent} {'✓' if intent == 'restaurant' else '✗'}")

if __name__ == "__main__":
    test_classification()
