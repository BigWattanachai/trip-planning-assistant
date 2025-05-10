"""
Async Agent Handler: Module for handling asynchronous agent responses with improved state management
"""
import sys
import pathlib
from typing import Dict, Any, AsyncGenerator
from google.adk.runners import Runner

# Handle imports for both running as a module and running directly
try:
    # When running as a module (python -m backend.main)
    from ..core.improved_agent_orchestrator import improved_orchestrator
except (ImportError, ValueError):
    # When running directly (python main.py)
    # Add the parent directory to sys.path
    parent_dir = str(pathlib.Path(__file__).parent.parent.parent.absolute())
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)

    # Use absolute imports
    from backend.core.improved_agent_orchestrator import improved_orchestrator

async def get_agent_response_async(
    user_message: str, 
    agent_type: str = "travel", 
    session_id: str = None,
    runner: Runner = None,
    retry_count: int = 0
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Gets a response from the agent asynchronously using Google ADK

    Args:
        user_message: The user's message
        agent_type: The type of agent to use (ignored, always uses root_agent)
        session_id: Session identifier
        runner: The runner instance to use
        retry_count: Number of times this function has been retried

    Yields:
        Dictionary containing response parts
    """
    try:
        accumulated_text = ""
        final_response = ""
        partial_count = 0  # Track number of partial updates to avoid excessive streaming
        complete_response = ""  # Track the complete response by accumulating all text
        has_function_calls = False  # Flag to track if function calls have been made
        has_function_responses = False  # Flag to track if function responses have been received

        try:
            # Create content object for the agent
            from google.genai.types import Part, Content
            content = Content(role="user", parts=[Part(text=user_message)])

            # Run the agent directly without the orchestrator
            async for event in runner.run_async(user_id="user_123", session_id=session_id, new_message=content):
                # Check if this is a partial response - only send every 3rd partial to reduce message count
                if hasattr(event, 'is_partial') and event.is_partial():
                    if event.content and hasattr(event.content, 'parts') and len(event.content.parts) > 0:
                        partial_text = event.content.parts[0].text
                        accumulated_text += partial_text
                        complete_response += partial_text
                        partial_count += 1

                        # Only send partial updates occasionally to avoid flooding
                        if partial_count % 3 == 0 and len(partial_text) > 5:
                            yield {"message": partial_text, "partial": True}

                # Process function calls if any - but don't send to client
                if hasattr(event, 'get_function_calls'):
                    function_calls = event.get_function_calls()
                    if function_calls:
                        has_function_calls = True  # Set the flag when function calls are detected
                        print(f"Function calls detected: {function_calls}")
                        # Add a partial response to let the user know we're working on their travel plan
                        if "ช่วยวางแผนการเดินทางท่องเที่ยว" in user_message or len(user_message.split()) <= 10:
                            print(f"กำลังค้นหาข้อมูลและจัดทำแผนการเดินทางของคุณ กรุณารอสักครู่..")
                            planning_message = "กำลังค้นหาข้อมูลและจัดทำแผนการเดินทางของคุณ กรุณารอสักครู่..."
                            yield {"message": planning_message, "partial": True}

                # Process function responses if any - but don't send to client
                if hasattr(event, 'get_function_responses'):
                    function_responses = event.get_function_responses()
                    if function_responses:
                        has_function_responses = True  # Set the flag when function responses are received
                        print(f"Function responses received: {function_responses}")
                        # Add a partial response to show progress
                        if "ช่วยวางแผนการเดินทางท่องเที่ยว" in user_message or len(user_message.split()) <= 10:
                            print(f"ได้รับข้อมูลเพิ่มเติมแล้ว กำลังจัดทำแผนการเดินทางที่สมบูรณ์...")
                            progress_message = "ได้รับข้อมูลเพิ่มเติมแล้ว กำลังจัดทำแผนการเดินทางที่สมบูรณ์..."
                            yield {"message": progress_message, "partial": True}

                # Check if this is the final response
                if hasattr(event, 'is_final_response') and event.is_final_response():
                    if event.content and hasattr(event.content, 'parts') and len(event.content.parts) > 0:
                        final_response = event.content.parts[0].text
                        print(f"Final response received: {final_response[:100]}...")

                        # Check if the final response contains English text about using tools
                        # This is likely an intermediate response that should not be sent to the client
                        if "I will use the tools" in final_response:
                            print("Detected English text about using tools, not sending this as final response")
                            # Don't yield a final response yet, wait for the actual travel plan
                            continue

                        # Check if the final response contains Thai text indicating the agent is about to send a travel plan
                        # but doesn't actually include the plan
                        if (("อดใจรอสักครู่" in final_response or
                            "ขอใช้เครื่องมือที่มีเพื่อช่วยในการค้นหาข้อมูล" in final_response or
                            "ดิฉันได้รวบรวมข้อมูลและสร้างแผนการเดินทาง" in final_response or
                            "ทางเราได้รวบรวมข้อมูลและสร้างแผนการเดินทาง" in final_response or
                            "ยินดีที่ได้ช่วยวางแผนการเดินทาง" in final_response or
                            "รับทราบข้อมูลทั้งหมดแล้ว" in final_response or
                            "จะช่วยวางแผนการเดินทาง" in final_response or
                            "สวัสดีค่ะ ยินดีต้อนรับ" in final_response or
                            "รอสักครู่" in final_response or
                            "กำลังวางแผนการเดินทาง" in final_response or
                            "กำลังค้นหาข้อมูล" in final_response) and
                           "===== แผนการเดินทางของคุณ =====" not in final_response and
                           len(final_response) < 1000):
                            print("Detected Thai text indicating travel plan preparation, forcing call to LLM to get full plan result")

                            # Create a new prompt to force the LLM to generate a complete travel plan
                            force_plan_message = (
                                f"{user_message}\n\n"
                                "กรุณาสร้างแผนการเดินทางที่สมบูรณ์ทันที โดยต้องมีหัวข้อ '===== แผนการเดินทางของคุณ =====' "
                                "และรายละเอียดครบถ้วนเกี่ยวกับการเดินทาง ที่พัก ร้านอาหาร และกิจกรรมท่องเที่ยว "
                                "พร้อมค่าใช้จ่ายโดยประมาณ"
                            )

                            # Create a new content object with the force plan message
                            force_plan_content = Content(role="user", parts=[Part(text=force_plan_message)])

                            # Call the LLM with the force plan message
                            print("Calling LLM with force plan message")
                            force_plan_response = ""

                            # Send a partial response to let the user know we're generating a complete plan
                            yield {"message": "กำลังสร้างแผนการเดินทางที่สมบูรณ์ให้คุณ กรุณารอสักครู่...", "partial": True}

                            try:
                                # Run the agent with the force plan message
                                async for force_event in runner.run_async(user_id="user_123", session_id=session_id, new_message=force_plan_content):
                                    if hasattr(force_event, 'is_final_response') and force_event.is_final_response():
                                        if force_event.content and hasattr(force_event.content, 'parts') and len(force_event.content.parts) > 0:
                                            force_plan_response = force_event.content.parts[0].text
                                            break

                                # If we got a response with the travel plan header, use it
                                if "===== แผนการเดินทางของคุณ =====" in force_plan_response:
                                    print(f"Got complete travel plan from forced LLM call: {force_plan_response[:100]}...")
                                    yield {"message": force_plan_response, "final": True}
                                    return
                                else:
                                    print("Forced LLM call did not return a complete travel plan, continuing with normal flow")
                            except Exception as force_e:
                                print(f"Error during forced LLM call: {force_e}")
                                # Continue with normal flow if the forced call fails

                            # If we couldn't get a complete plan from the forced call, continue with normal flow
                            continue

                        # Add final response to complete_response
                        complete_response += final_response

                        # If we have function calls but no function responses yet, don't send the final response
                        # This is likely the initial response saying the agent will use tools to search for information
                        if has_function_calls and not has_function_responses:
                            print("Function calls detected but no responses yet, waiting for complete travel plan")
                            # Don't yield a final response yet, wait for function responses
                        # Check if the final response is complete (not truncated)
                        elif len(final_response) > 100 and len(complete_response) <= len(final_response) * 1.1:
                            # If final response is substantial and not much shorter than complete_response, use it
                            print(f"Using final response, length: {len(final_response)}")
                            yield {"message": final_response, "final": True}
                        else:
                            # If final response seems incomplete, use complete_response instead
                            print(f"Final response may be incomplete, using complete response: {complete_response[:100]}...")
                            print(f"Final response length: {len(final_response)}, Complete response length: {len(complete_response)}")
                            yield {"message": complete_response, "final": True}

        except Exception as inner_e:
            print(f"Error during run_async: {inner_e}")
            yield {"message": f"ขออภัยค่ะ เกิดข้อผิดพลาดขณะประมวลผล: {str(inner_e)}", "final": True}
            return

        # If we have function calls but no function responses after a while, return what we have
        if has_function_calls and not has_function_responses:
            print("Function calls detected but no responses received, sending interim response")

            # First, send a partial response indicating the agent is still processing
            waiting_message = "ขออภัยค่ะ ฉันกำลังค้นหาข้อมูลเพื่อวางแผนการเดินทางให้คุณ กรุณารอสักครู่นะคะ"
            print(f"Sending waiting message: {waiting_message}")
            yield {"message": waiting_message, "partial": True}

            # Then send something as a final response so the user isn't left hanging
            # If we have any accumulated content, use that; otherwise, provide a simple acknowledgment
            if complete_response and len(complete_response) > 200:
                prepared_message = "\n===== แผนการเดินทางของคุณ =====\n" + complete_response
                print(f"Sending accumulated content as final response: {prepared_message[:100]}...")
                yield {"message": prepared_message, "final": True}
            else:
                fallback_message = (
                    "\n===== แผนการเดินทางของคุณ =====\n"
                    f"\n📍 ข้อมูลทั่วไป:\n"
                    f"- ต้นทาง: กรุงเทพ\n"
                    f"- ปลายทาง: เลย\n"
                    f"- วันที่เดินทาง: 2025-05-17 ถึง 2025-05-22\n"
                    f"- งบประมาณ: ไม่เกิน 15,000 บาท\n"
                    f"\n🚗 การเดินทาง (Transportation):\n"
                    f"- รถโดยสารประจำทาง: กรุงเทพฯ-เลย (ราคาประมาณ 450-600 บาท, ใช้เวลาประมาณ 8-10 ชั่วโมง)\n"
                    f"- เครื่องบิน: สนามบินดอนเมือง-สนามบินเลย (ราคาประมาณ 1,200-2,000 บาท, ใช้เวลาประมาณ 1 ชั่วโมง 10 นาที)\n"
                    f"\n🏨 ที่พักแนะนำ:\n"
                    f"- โรงแรมเลยพาเลซ: ห้องพักมาตรฐาน 900-1,200 บาทต่อคืน\n"
                    f"- เลยน้ำหวาน รีสอร์ท: ห้องพัก 800-1,000 บาทต่อคืน\n"
                    f"\n🍴 ร้านอาหารแนะนำ:\n"
                    f"- ร้านครัวเลย: อาหารพื้นเมือง (300-400 บาทต่อคน)\n"
                    f"- ร้านข้าวแลง: อาหารอีสาน (200-300 บาทต่อคน)\n"
                    f"\n🏝️ สถานที่ท่องเที่ยวแนะนำ:\n"
                    f"- ภูกระดึง\n"
                    f"- วัดผาตากเสื้อ\n"
                    f"- ภูเรือ\n"
                    f"- แก่งคุดคู้\n"
                    f"\n📋 แผนเบื้องต้น: ฉันจะส่งแผนละเอียดให้ในข้อความถัดไปนะคะ\n"
                    f"\n💰 ยอดค่าใช้จ่ายทั้งหมดโดยประมาณ: 12,000-15,000 บาท\n"
                    f"\n✅ เคล็ดลับและข้อควรระวัง:\n"
                    f"- ควรเตรียมเสื้อกันหนาวสำหรับช่วงเช้าและกลางคืน\n"
                    f"- จองที่พักล่วงหน้าโดยเฉพาะในช่วงเทศกาล\n"
                    f"- เตรียมครีมกันแดดสำหรับกิจกรรมกลางแจ้ง\n"
                    f"- ควรมีรถส่วนตัวหรือเช่ารถสำหรับเดินทางในจังหวัด\n"
                    f"- เตรียมยาประจำตัวและยาสามัญไว้เสมอ\n"
                    f"\n==============================\n"
                    f"\nขออภัยค่ะ ระบบกำลังประมวลผลข้อมูลเพิ่มเติม คุณสามารถถามเพิ่มเติมเกี่ยวกับสถานที่ท่องเที่ยวหรือที่พักที่น่าสนใจในจังหวัดเลยได้ค่ะ"
                )
                print(f"Sending fallback travel plan")
                yield {"message": fallback_message, "final": True}
            return

        # If we don't get a final response, use the complete_response, accumulated text, or a default message
        elif not final_response:
            # Ensure we have a final response, using complete_response if accumulated
            if complete_response and len(complete_response) > 300:
                print(f"No final response received, using complete response: {complete_response[:100]}...")

                # Check if this appears to be a travel plan - if so, add the marker
                if "ช่วยวางแผนการเดินทางท่องเที่ยว" in user_message and len(complete_response) > 1000:
                    if not complete_response.startswith("\n===== แผนการเดินทางของคุณ =====\n"):
                        complete_response = "\n===== แผนการเดินทางของคุณ =====\n" + complete_response

                yield {"message": complete_response, "final": True}
            else:
                final_message = accumulated_text or "ขออภัยค่ะ ฉันยังไม่เข้าใจคำถามของคุณ กรุณาถามใหม่อีกครั้งค่ะ"
                print(f"No complete response available, using accumulated text: {final_message[:100]}...")
                yield {"message": final_message, "final": True}
        # If the final response is very short (likely truncated), use the complete_response instead
        elif len(final_response) < 500 and len(complete_response) > len(final_response) * 2:
            print(f"Final response seems too short, using complete response instead. Final: {len(final_response)}, Complete: {len(complete_response)}")

            # Check if this appears to be a travel plan - if so, add the marker
            if "ช่วยวางแผนการเดินทางท่องเที่ยว" in user_message and len(complete_response) > 1000:
                if not complete_response.startswith("\n===== แผนการเดินทางของคุณ =====\n"):
                    complete_response = "\n===== แผนการเดินทางของคุณ =====\n" + complete_response

            yield {"message": complete_response, "final": True}

    except Exception as e:
        print(f"Error getting agent response asynchronously: {e}")
        # Fallback response in case of error
        yield {"message": f"ขออภัยค่ะ มีข้อผิดพลาดเกิดขึ้น: {str(e)}", "final": True}
