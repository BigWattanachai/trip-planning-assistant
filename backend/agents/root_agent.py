from agents.travel.tools.sub_agent_tools import (
    call_activity_agent,
    call_restaurant_agent,
    call_accommodation_agent,
    call_transportation_agent
)

class RootAgent:
    def __init__(self):
        pass

    def delegate(self, query: str, context: str = "") -> str:
        """
        Delegates tasks to sub-agents based on the query/context.
        Aggregates and formats the results into a user-friendly travel plan.
        """
        results = {}
        results['activity'] = call_activity_agent(query, context)
        results['restaurant'] = call_restaurant_agent(query, context)
        results['accommodation'] = call_accommodation_agent(query, context)
        results['transportation'] = call_transportation_agent(query, context)

        # Extract response text from each sub-agent result
        activity_text = results['activity'].get('response', '')
        restaurant_text = results['restaurant'].get('response', '')
        accommodation_text = results['accommodation'].get('response', '')
        transportation_text = results['transportation'].get('response', '')

        # Combine results into a formatted travel plan
        travel_plan = (
            "\n===== แผนการเดินทางของคุณ =====\n"
            "\n\U0001F697 การเดินทาง (Transportation):\n" + (transportation_text or "- ไม่มีข้อมูลการเดินทาง") +
            "\n\U0001F3E8 ที่พักแนะนำ (Accommodation):\n" + (accommodation_text or "- ไม่มีข้อมูลที่พัก") +
            "\n\U0001F374 ร้านอาหารแนะนำ (Restaurants):\n" + (restaurant_text or "- ไม่มีข้อมูลร้านอาหาร") +
            "\n\U0001F3D6\uFE0F กิจกรรมและสถานที่ท่องเที่ยว (Activities):\n" + (activity_text or "- ไม่มีข้อมูลกิจกรรมหรือสถานที่ท่องเที่ยว") +
            "\n==============================\n"
        )
        return travel_plan
