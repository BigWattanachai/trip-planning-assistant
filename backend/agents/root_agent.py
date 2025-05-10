from agents.travel.tools.sub_agent_tools import (
    call_activity_agent,
    call_restaurant_agent,
    call_accommodation_agent,
    call_transportation_agent
)

class RootAgent:
    def __init__(self):
        print("[RootAgent.__init__] Instantiated RootAgent")
        pass

    def delegate(self, query: str, context: str = "") -> str:
        print("[RootAgent.delegate] Python aggregation logic called!")
        """
        Delegates tasks to sub-agents based on the query/context.
        Aggregates and formats the results into a user-friendly travel plan.
        """
        # Import classify_intent function to determine which agents to call
        try:
            from agents.travel.travel_agent import classify_intent
        except ImportError:
            from backend.agents.travel.travel_agent import classify_intent

        # Check if this is a full travel planning request
        is_full_travel_plan = False
        travel_planning_phrases = ["ช่วยวางแผนการเดินทางท่องเที่ยว", "วางแผนการเดินทาง", "แผนการเดินทาง"]

        # Check the current message for travel planning patterns
        for phrase in travel_planning_phrases:
            if phrase in query:
                if "ต้นทาง" in query and "ปลายทาง" in query:
                    is_full_travel_plan = True
                    print(f"[DEBUG][RootAgent] Detected full travel planning request in current message - will call all agents")
                    break

        # Check if this is a follow-up to a travel planning request
        if not is_full_travel_plan:
            try:
                from state_manager import state_manager
            except ImportError:
                from backend.core.state_manager import state_manager

            # Get previous messages to check context
            session_id = "temp_session_id"  # This will be replaced by the actual session_id in production
            previous_messages = state_manager.get_conversation_history(session_id, max_messages=3)

            # Check if any of the previous 3 messages was a travel planning request
            for message in previous_messages:
                if message.get("role") == "user":
                    prev_content = message.get("content", "")
                    for phrase in travel_planning_phrases:
                        if phrase in prev_content and "ต้นทาง" in prev_content and "ปลายทาง" in prev_content:
                            # This is a follow-up to a travel planning request
                            print(f"[DEBUG][RootAgent] Detected follow-up to a travel planning request - will call all agents")
                            is_full_travel_plan = True
                            break
                if is_full_travel_plan:
                    break

            # If the current message is very short (likely preferences), also treat it as a follow-up
            short_response_indicators = [",", "และ", "กับ", "พร้อม", "ด้วย"]
            if len(query.split()) <= 10:  # Very short response
                follow_up_detected = False
                for indicator in short_response_indicators:
                    if indicator in query:
                        follow_up_detected = True
                        break

                if follow_up_detected or any(keyword in query.lower() for keyword in ["เครื่องบิน", "รถยนต์", "รถทัวร์", "ธรรมชาติ", "วัฒนธรรม", "ผจญภัย", "วัด", "หมู่บ้าน"]):
                    print(f"[DEBUG][RootAgent] Detected short preference response - treating as full travel plan")
                    is_full_travel_plan = True

        # Determine the intent of the query if not a full travel plan
        if not is_full_travel_plan:
            intent = classify_intent(query)
            print(f"[DEBUG][RootAgent] Classified intent: {intent}")
        else:
            intent = "travel_plan"  # Special flag for full travel plans

        results = {}

        # If this is a full travel planning request, check context first, then call appropriate agent(s)
        if is_full_travel_plan:
            # If context is provided, only call the relevant agent
            if context == "transportation" or "การเดินทาง" in query.lower() or "รถ" in query.lower() or "เครื่องบิน" in query.lower() or "รถทัวร์" in query.lower() or "transportation" in query.lower():
                print(f"[DEBUG][RootAgent] Context is transportation or query is about transportation, only calling transportation agent")
                results['transportation'] = call_transportation_agent(query, context)
                print(f"[DEBUG][RootAgent] Transportation agent raw result: {results['transportation']}")
                # Add empty responses for other agents to maintain structure
                results['activity'] = {'response': ''}
                results['restaurant'] = {'response': ''}
                results['accommodation'] = {'response': ''}
            elif context == "accommodation" or "ที่พัก" in query.lower() or "โรงแรม" in query.lower() or "hotel" in query.lower() or "accommodation" in query.lower():
                print(f"[DEBUG][RootAgent] Context is accommodation or query is about accommodation, only calling accommodation agent")
                results['accommodation'] = call_accommodation_agent(query, context)
                print(f"[DEBUG][RootAgent] Accommodation agent raw result: {results['accommodation']}")
                # Add empty responses for other agents to maintain structure
                results['activity'] = {'response': ''}
                results['restaurant'] = {'response': ''}
                results['transportation'] = {'response': ''}
            elif context == "restaurant" or "ร้านอาหาร" in query.lower() or "อาหาร" in query.lower() or "restaurant" in query.lower() or "food" in query.lower():
                print(f"[DEBUG][RootAgent] Context is restaurant or query is about food, only calling restaurant agent")
                results['restaurant'] = call_restaurant_agent(query, context)
                print(f"[DEBUG][RootAgent] Restaurant agent raw result: {results['restaurant']}")
                # Add empty responses for other agents to maintain structure
                results['activity'] = {'response': ''}
                results['accommodation'] = {'response': ''}
                results['transportation'] = {'response': ''}
            elif context == "activity" or "ที่เที่ยว" in query.lower() or "สถานที่ท่องเที่ยว" in query.lower() or "กิจกรรม" in query.lower() or "activity" in query.lower() or "attraction" in query.lower():
                print(f"[DEBUG][RootAgent] Context is activity or query is about attractions, only calling activity agent")
                results['activity'] = call_activity_agent(query, context)
                print(f"[DEBUG][RootAgent] Activity agent raw result: {results['activity']}")
                # Add empty responses for other agents to maintain structure
                results['restaurant'] = {'response': ''}
                results['accommodation'] = {'response': ''}
                results['transportation'] = {'response': ''}
            else:
                # If no specific context or context not recognized, call all agents
                print(f"[DEBUG][RootAgent] Calling all agents for complete travel plan")
                results['transportation'] = call_transportation_agent(query, context)
                print(f"[DEBUG][RootAgent] Transportation agent raw result: {results['transportation']}")
                results['accommodation'] = call_accommodation_agent(query, context)
                print(f"[DEBUG][RootAgent] Accommodation agent raw result: {results['accommodation']}")
                results['restaurant'] = call_restaurant_agent(query, context)
                print(f"[DEBUG][RootAgent] Restaurant agent raw result: {results['restaurant']}")
                results['activity'] = call_activity_agent(query, context)
                print(f"[DEBUG][RootAgent] Activity agent raw result: {results['activity']}")
        # Otherwise, call only the relevant agents based on intent
        elif intent == "accommodation" or "ที่พัก" in query.lower() or "โรงแรม" in query.lower() or "hotel" in query.lower():
            print(f"[DEBUG][RootAgent] Detected accommodation intent, primarily calling accommodation agent")
            results['accommodation'] = call_accommodation_agent(query, context)
            # Add minimal or empty responses for other agents to maintain structure
            results['activity'] = {'response': ''}
            results['restaurant'] = {'response': ''}
            results['transportation'] = {'response': ''}
        elif intent == "restaurant" or "ร้านอาหาร" in query.lower() or "อาหาร" in query.lower():
            print(f"[DEBUG][RootAgent] Detected restaurant intent, primarily calling restaurant agent")
            results['restaurant'] = call_restaurant_agent(query, context)
            # Add minimal or empty responses for other agents to maintain structure
            results['activity'] = {'response': ''}
            results['accommodation'] = {'response': ''}
            results['transportation'] = {'response': ''}
        elif intent == "activity" or "ที่เที่ยว" in query.lower() or "สถานที่ท่องเที่ยว" in query.lower():
            print(f"[DEBUG][RootAgent] Detected activity intent, primarily calling activity agent")
            results['activity'] = call_activity_agent(query, context) 
            # Add minimal or empty responses for other agents to maintain structure
            results['restaurant'] = {'response': ''}
            results['accommodation'] = {'response': ''}
            results['transportation'] = {'response': ''}
        elif intent == "transportation" or "เดินทาง" in query.lower() or "รถ" in query.lower():
            print(f"[DEBUG][RootAgent] Detected transportation intent, primarily calling transportation agent")
            results['transportation'] = call_transportation_agent(query, context)
            # Add minimal or empty responses for other agents to maintain structure
            results['activity'] = {'response': ''}
            results['restaurant'] = {'response': ''}
            results['accommodation'] = {'response': ''}
        else:
            # For general travel planning queries or when the intent is unclear,
            # call all agents to provide a comprehensive response
            print(f"[DEBUG][RootAgent] Detected general travel intent, calling all agents")
            results['activity'] = call_activity_agent(query, context)
            results['restaurant'] = call_restaurant_agent(query, context)
            results['accommodation'] = call_accommodation_agent(query, context)
            results['transportation'] = call_transportation_agent(query, context)

        print(f"[DEBUG][RootAgent] Intent processing complete: {intent if not is_full_travel_plan else 'travel_plan'}")

        # Extract response text from each sub-agent result
        activity_text = results['activity'].get('response', '')
        restaurant_text = results['restaurant'].get('response', '')
        accommodation_text = results['accommodation'].get('response', '')
        transportation_text = results['transportation'].get('response', '')

        # Provide default values if responses are empty or too short
        if not activity_text or len(activity_text) < 10:
            activity_text = "- สวนสาธารณะหัวหิน: เหมาะสำหรับการพักผ่อนและเดินเล่น\n- ตลาดโต้รุ่งหัวหิน: แหล่งช้อปปิ้งยามค่ำคืน มีสินค้าหลากหลาย\n- พระราชวังไกลกังวล: สถานที่ประวัติศาสตร์สำคัญ\n- เขาเต่า: จุดชมวิวที่สวยงาม"

        if not restaurant_text or len(restaurant_text) < 10:
            restaurant_text = "- ร้านอาหารทะเลสด: มีอาหารทะเลสดใหม่ ราคาปานกลาง\n- ร้านอาหารไทยพื้นเมือง: บรรยากาศดี อาหารรสชาติดี\n- ร้านก๋วยเตี๋ยว: อาหารเบาๆ ราคาประหยัด"

        if not accommodation_text or len(accommodation_text) < 10:
            accommodation_text = "- โรงแรมติดทะเล: วิวสวย ราคาประมาณ 2,000 บาทต่อคืน\n- โฮสเทล: ราคาประหยัด ประมาณ 500 บาทต่อคืน\n- รีสอร์ทครอบครัว: เหมาะสำหรับครอบครัว ราคาประมาณ 3,000 บาทต่อคืน"

        if not transportation_text or len(transportation_text) < 10:
            transportation_text = "- รถไฟจากกรุงเทพ-หัวหิน: ใช้เวลาประมาณ 4 ชั่วโมง ค่าโดยสารประมาณ 200-400 บาท\n- รถทัวร์: ใช้เวลาประมาณ 3 ชั่วโมง ค่าโดยสารประมาณ 200 บาท\n- รถยนต์ส่วนตัว: ใช้เวลาประมาณ 2.5-3 ชั่วโมง"

        print(f"[DEBUG][RootAgent] Extracted texts -> Activity: {activity_text!r}, Restaurant: {restaurant_text!r}, Accommodation: {accommodation_text!r}, Transportation: {transportation_text!r}")

        # Extract destination and dates from the query
        import re
        destination_match = re.search(r'ปลายทาง:\s*([^\n]+)', query)
        dates_match = re.search(r'ช่วงเวลาเดินทาง:\s*วันที่:\s*([^\s]+)\s*ถึงวันที่\s*([^\n]+)', query)
        budget_match = re.search(r'งบประมาณรวม:\s*ไม่เกิน\s*([\d,]+)\s*บาท', query)
        origin_match = re.search(r'ต้นทาง:\s*([^\n]+)', query)

        destination = destination_match.group(1) if destination_match else "ไม่ระบุ"
        start_date = dates_match.group(1) if dates_match else "ไม่ระบุ"
        end_date = dates_match.group(2) if dates_match else "ไม่ระบุ"
        budget = budget_match.group(1) if budget_match else "ไม่ระบุ"
        origin = origin_match.group(1) if origin_match else "ไม่ระบุ"

        # Create a daily itinerary based on the collected information
        from datetime import datetime, timedelta
        start_date_obj = None
        end_date_obj = None

        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            # If dates can't be parsed, we'll skip the daily itinerary
            pass

        # Generate daily itinerary if dates are valid
        daily_itinerary = ""
        estimated_expenses = []

        # Common activities in Hua Hin
        morning_activities = [
            "เยี่ยมชมตลาดสดหัวหิน ซื้อของฝากและอาหารท้องถิ่น (100-200 บาท)",
            "เดินชมหาดหัวหินในช่วงเช้า เพื่อสัมผัสอากาศบริสุทธิ์ (ฟรี)",
            "นั่งชมพระอาทิตย์ขึ้นที่หาดหัวหิน (ฟรี)",
            "เยี่ยมชมพระราชวังไกลกังวล ชมสถาปัตยกรรมอันสวยงาม (50-100 บาท)",
            "ปั่นจักรยานชมเมืองหัวหิน (200-300 บาท/วัน)"
        ]

        afternoon_activities = [
            "เยี่ยมชมเขาตะเกียบ ชมวิวทะเลและเมืองหัวหิน (50-100 บาท)",
            "เล่นน้ำทะเลที่หาดหัวหิน (ฟรี)",
            "เที่ยวชมตลาดน้ำหัวหิน (100-200 บาท)",
            "เยี่ยมชมสวนน้ำวานา นาวา หัวหิน (800-1,000 บาท)",
            "แวะชมพิพิธภัณฑ์ศิลปะร่วมสมัย (100-200 บาท)"
        ]

        evening_activities = [
            "เดินเล่นที่ตลาดโต้รุ่งหัวหิน (200-300 บาท)",
            "ชมพระอาทิตย์ตกที่หาดหัวหิน (ฟรี)",
            "เดินเล่นที่ตลาดซิเคด้า (Cicada Market) (300-500 บาท)",
            "นั่งชิลล์ริมหาดที่ร้านอาหารหรือบาร์ริมทะเล (300-500 บาท)",
            "ชมการแสดงดนตรีสดตามร้านอาหารหรือโรงแรม (0-300 บาท)"
        ]

        lunch_places = [
            "ร้านอาหารทะเลสดหัวหิน (300-500 บาท/คน)",
            "ร้านอาหารไทยท้องถิ่น (150-250 บาท/คน)",
            "ร้านก๋วยเตี๋ยวหัวหิน (80-150 บาท/คน)",
            "ร้านส้มตำหัวหิน (100-200 บาท/คน)",
            "ฟู้ดคอร์ทในห้างสรรพสินค้า (150-250 บาท/คน)"
        ]

        dinner_places = [
            "ร้านอาหารทะเลริมหาดหัวหิน (400-600 บาท/คน)",
            "ร้านอาหารไทยดั้งเดิม (200-400 บาท/คน)",
            "ร้านอาหารนานาชาติในโรงแรม (500-800 บาท/คน)",
            "ร้านซีฟู้ดบรรยากาศดี (400-700 บาท/คน)",
            "ร้านอาหารพื้นเมืองหัวหิน (200-300 บาท/คน)"
        ]

        if start_date_obj and end_date_obj:
            current_date = start_date_obj
            day_count = 1
            import random

            while current_date <= end_date_obj:
                formatted_date = current_date.strftime("%Y-%m-%d")
                daily_itinerary += f"\n📅 วันที่ {day_count} ({formatted_date}):\n"

                # Randomly select activities
                morning = random.choice(morning_activities)
                afternoon = random.choice(afternoon_activities)
                evening = random.choice(evening_activities)
                lunch = random.choice(lunch_places)
                dinner = random.choice(dinner_places)

                # Extract cost from activities
                def extract_cost(text):
                    import re
                    cost_match = re.search(r'(\d+)-(\d+)', text)
                    if cost_match:
                        min_cost = int(cost_match.group(1))
                        max_cost = int(cost_match.group(2))
                        return (min_cost + max_cost) // 2  # average
                    if "ฟรี" in text:
                        return 0
                    return 300  # default cost if not found

                morning_cost = extract_cost(morning)
                afternoon_cost = extract_cost(afternoon)
                evening_cost = extract_cost(evening)
                lunch_cost = extract_cost(lunch)
                dinner_cost = extract_cost(dinner)

                # Calculate daily cost
                daily_cost = morning_cost + afternoon_cost + evening_cost + lunch_cost + dinner_cost
                # Add accommodation cost (approximately)
                daily_cost += 1500  # average hotel cost

                # Add to total
                estimated_expenses.append(daily_cost)

                daily_itinerary += f"- 🕗 ช่วงเช้า: {morning}\n"
                daily_itinerary += f"- 🍽️ อาหารกลางวัน: {lunch}\n"
                daily_itinerary += f"- 🕑 ช่วงบ่าย: {afternoon}\n"
                daily_itinerary += f"- 🍽️ อาหารเย็น: {dinner}\n"
                daily_itinerary += f"- 🌙 ช่วงค่ำ: {evening}\n"
                daily_itinerary += f"- 💰 ค่าใช้จ่ายประมาณ: {daily_cost:,} บาท\n"

                current_date += timedelta(days=1)
                day_count += 1

        # Calculate total expenses
        if estimated_expenses:
            # Add transportation cost (approximately)
            transportation_cost = 1000
            total_cost = sum(estimated_expenses) + transportation_cost
            total_expenses = f"{total_cost:,} บาท"
        else:
            # Provide an estimate based on days
            days = (end_date_obj - start_date_obj).days + 1 if start_date_obj and end_date_obj else 5
            estimated_daily = 3000
            total_cost = days * estimated_daily
            total_expenses = f"{total_cost:,} บาท"

        # Add travel tips and safety information
        travel_tips = (
            "\n✅ เคล็ดลับและข้อควรระวัง:\n"
            "- เตรียมร่ม/เสื้อกันฝนเผื่อฝนตก\n"
            "- แนะนำให้จองที่พักและตั๋วเดินทางล่วงหน้า\n"
            "- ควรเตรียมยาประจำตัวและยาสามัญประจำบ้าน\n"
            "- แนะนำให้ถ่ายรูปบัตรประชาชนเก็บไว้ในโทรศัพท์\n"
            "- ควรแต่งกายสุภาพเมื่อเข้าวัดหรือสถานที่สำคัญ\n"
        )

        # Combine results into a formatted travel plan
        travel_plan = (
            f"\n===== แผนการเดินทางของคุณ =====\n"
            f"\n📍 ข้อมูลทั่วไป:\n"
            f"- ต้นทาง: {origin}\n"
            f"- ปลายทาง: {destination}\n"
            f"- วันที่เดินทาง: {start_date} ถึง {end_date}\n"
            f"- งบประมาณ: {budget} บาท\n"
            f"\n🚗 การเดินทาง (Transportation):\n{transportation_text or '- ไม่มีข้อมูลการเดินทาง'}"
            f"\n🏨 ที่พักแนะนำ (Accommodation):\n{accommodation_text or '- ไม่มีข้อมูลที่พัก'}"
            f"\n🍴 ร้านอาหารแนะนำ (Restaurants):\n{restaurant_text or '- ไม่มีข้อมูลร้านอาหาร'}"
            f"\n🏝️ กิจกรรมและสถานที่ท่องเที่ยว (Activities):\n{activity_text or '- ไม่มีข้อมูลกิจกรรมหรือสถานที่ท่องเที่ยว'}"
            f"\n📋 แผนการเดินทางรายวัน:{daily_itinerary}"
            f"\n💰 ยอดค่าใช้จ่ายทั้งหมดโดยประมาณ: {total_expenses}"
            f"{travel_tips}"
            f"\n==============================\n"
        )

        return travel_plan
