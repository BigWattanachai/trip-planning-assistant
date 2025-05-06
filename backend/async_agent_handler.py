"""
Async Agent Handler: Module for handling asynchronous agent responses with improved state management
"""
from typing import Dict, Any, AsyncGenerator
from google.adk.runners import Runner
from improved_agent_orchestrator import improved_orchestrator

async def get_agent_response_async(
    user_message: str, 
    agent_type: str = "travel", 
    session_id: str = None,
    runner: Runner = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Gets a response from the agent asynchronously using Google ADK and the improved orchestrator

    Args:
        user_message: The user's message
        agent_type: The type of agent to use
        session_id: Session identifier
        runner: The runner instance to use

    Yields:
        Dictionary containing response parts
    """
    try:
        accumulated_text = ""
        final_response = ""
        partial_count = 0  # Track number of partial updates to avoid excessive streaming

        try:
            # Use the improved orchestrator to process the message and get events
            async for event in improved_orchestrator.process_message(user_message, session_id, runner):
                # Check if this is a partial response - only send every 3rd partial to reduce message count
                if hasattr(event, 'is_partial') and event.is_partial():
                    if event.content and hasattr(event.content, 'parts') and len(event.content.parts) > 0:
                        partial_text = event.content.parts[0].text
                        accumulated_text += partial_text
                        partial_count += 1

                        # Only send partial updates occasionally to avoid flooding
                        if partial_count % 3 == 0 and len(partial_text) > 5:
                            yield {"message": partial_text, "partial": True}

                # Check if this is the final response
                if hasattr(event, 'is_final_response') and event.is_final_response():
                    if event.content and hasattr(event.content, 'parts') and len(event.content.parts) > 0:
                        final_response = event.content.parts[0].text
                        yield {"message": final_response, "final": True}

                # Process function calls if any - but don't send to client
                if hasattr(event, 'get_function_calls'):
                    function_calls = event.get_function_calls()

                # Process function responses if any - but don't send to client
                if hasattr(event, 'get_function_responses'):
                    function_responses = event.get_function_responses()

        except Exception as inner_e:
            print(f"Error during run_async: {inner_e}")
            yield {"message": f"ขออภัยค่ะ เกิดข้อผิดพลาดขณะประมวลผล: {str(inner_e)}", "final": True}
            return

        # If we don't get a final response, use the accumulated text or a default message
        if not final_response:
            final_message = accumulated_text or "ขออภัยค่ะ ฉันยังไม่เข้าใจคำถามของคุณ กรุณาถามใหม่อีกครั้งค่ะ"
            yield {"message": final_message, "final": True}

    except Exception as e:
        print(f"Error getting agent response asynchronously: {e}")
        # Fallback response in case of error
        yield {"message": f"ขออภัยค่ะ มีข้อผิดพลาดเกิดขึ้น: {str(e)}", "final": True}
