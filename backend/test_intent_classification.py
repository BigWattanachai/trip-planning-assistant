"""
Test script for intent classification.
"""
from agents.travel_agent import classify_intent

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

if __name__ == "__main__":
    test_classification()
