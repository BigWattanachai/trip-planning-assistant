#!/usr/bin/env python
"""
Test script for activity agent with Tavily search
"""

import os
import sys
import pathlib

# Add parent directory to sys.path
parent_dir = str(pathlib.Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

print("Loading dependencies and initializing Tavily...")

# Import Tavily search function if available
try:
    from sub_agents.activity_agent import activity_tavily_search
    tavily_available = activity_tavily_search is not None
    print(f"Tavily search available: {tavily_available}")
    
    if tavily_available:
        # Test with a simple query
        test_destination = "Bangkok"
        print(f"\nTesting Tavily search for activities in {test_destination}...")
        
        results = activity_tavily_search("popular tourist attractions", location=test_destination)
        
        if results:
            print("✅ Tavily search successful!")
            print(f"Result type: {type(results)}")
            print(f"Result length: {len(str(results))} characters")
            print("\nPreview of results:")
            print("-" * 60)
            preview = str(results)[:500] + "..." if len(str(results)) > 500 else str(results)
            print(preview)
            print("-" * 60)
        else:
            print("❌ No results returned from Tavily search")
    
    # Now test the agent through the main system
    print("\nTesting activity agent through the direct API...")
    from agent import call_sub_agent
    
    # Create a test query
    test_query = """
    ฉันกำลังวางแผนเดินทางไป กรุงเทพ 
    ในวันที่ 2025-05-20 ถึง 2025-05-23
    มีงบประมาณทั้งหมด 5,000 บาท
    
    ช่วยแนะนำสถานที่ท่องเที่ยวสำคัญและกิจกรรมที่น่าสนใจได้ไหม?
    ต้องการเน้นสถานที่สำคัญทางวัฒนธรรม ธรรมชาติ และจุดถ่ายรูปยอดนิยม
    """
    
    print("Calling activity agent with test query...")
    response = call_sub_agent("activity", test_query)
    
    if response and not response.startswith("Error"):
        print("\n✅ Activity agent call successful!")
        print("\nPreview of agent response:")
        print("-" * 60)
        preview = response[:1000] + "..." if len(response) > 1000 else response
        print(preview)
        print("-" * 60)
    else:
        print(f"\n❌ Error calling activity agent: {response}")
        
except ImportError as e:
    print(f"❌ Failed to import activity_tavily_search: {e}")
    print("Please ensure you've installed the required packages:")
    print("pip install langchain>=0.1.0 langchain-community>=0.1.0 tavily-python>=0.2.8")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTest completed!")
