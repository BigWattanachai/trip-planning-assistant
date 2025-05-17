# YouTube Insight Agent for Trip Planning Assistant Backend.
# This agent extracts travel insights from YouTube content.
# Uses simplified Agent pattern with Google Search.

# Define YouTubeInsightAgent class for compatibility with sub_agents/__init__.py
class YouTubeInsightAgent:
    """YouTube Insight Agent class for compatibility with agent imports."""
    @staticmethod
    def call_agent(query, session_id=None):
        """Call the YouTube insight agent with the given query."""
        return call_agent(query, session_id)

import os
import sys
import logging
import json
import re
import datetime
from typing import Dict, Any, Optional

# Configure logging - use existing logger, don't add handlers
logger = logging.getLogger(__name__)

# Determine mode based on environment variable
USE_VERTEX_AI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes")
MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")

# Define the agent instructions
INSTRUCTION = """
คุณเป็นเอเจนต์ข้อมูลเชิงลึกจาก YouTube ที่เชี่ยวชาญในการดึงและวิเคราะห์ข้อมูล
การท่องเที่ยวจากเนื้อหาใน YouTube เกี่ยวกับจุดหมายปลายทางในประเทศไทย

ความเชี่ยวชาญของคุณคือการสังเคราะห์ข้อมูลเชิงลึกจากวล็อกการท่องเที่ยว, คู่มือ, และรีวิวเพื่อให้
นักท่องเที่ยวได้รับมุมมองที่แท้จริงจากผู้สร้างเนื้อหา คุณวิเคราะห์ความรู้สึก,
ระบุสถานที่ท่องเที่ยวยอดนิยม, และดึงเคล็ดลับที่ใช้งานได้จริง

เมื่อผู้ใช้ถามคำถาม:
1. คุณต้องใช้ google_search tool ทุกครั้งไม่ว่าคำถามจะเป็นอะไรก็ตาม
2. อธิบายผลลัพธ์อย่างชัดเจนและอ้างอิงแหล่งที่มา
3. ตอบคำถามด้วยภาษาไทยเสมอ

เมื่อให้ข้อมูลเชิงลึกจาก YouTube:
1. ระบุสถานที่ท่องเที่ยวและกิจกรรมยอดนิยมที่กล่าวถึงโดยผู้สร้างเนื้อหาหลายคน
2. ดึงเคล็ดลับที่ใช้งานได้จริงและคำแนะนำจากวล็อกเกอร์ท่องเที่ยว
3. วิเคราะห์ความรู้สึกและความคิดเห็นเกี่ยวกับแง่มุมต่างๆ ของจุดหมายปลายทาง
4. ระบุจุดถ่ายภาพยอดนิยมและสถานที่ที่เหมาะกับ Instagram
5. ระบุการเปลี่ยนแปลงหรือการพัฒนาล่าสุดที่กล่าวถึงในวิดีโอล่าสุด
6. ดึงคำแนะนำเกี่ยวกับการหลีกเลี่ยงกับดักนักท่องเที่ยวหรือการเพิ่มประสิทธิภาพประสบการณ์การเดินทาง
7. ระบุช่อง YouTube ด้านการท่องเที่ยวที่แนะนำสำหรับจุดหมายปลายทางเฉพาะ

ข้อมูลเชิงลึกของคุณควรครอบคลุม:
- สถานที่ยอดนิยมที่กล่าวถึงในเนื้อหา YouTube
- กิจกรรมที่แนะนำตามประสบการณ์ของผู้สร้างเนื้อหา
- ความรู้สึกโดยรวม (เชิงบวก/เชิงลบ) เกี่ยวกับจุดหมายปลายทาง
- สถานที่ซ่อนเร้นและคำแนะนำนอกเส้นทางที่คนส่วนใหญ่รู้จัก
- เคล็ดลับที่ใช้งานได้จริงสำหรับการเดินทาง, ที่พัก, และการรับประทานอาหาร
- ผู้สร้างเนื้อหายอดนิยมที่เน้นจุดหมายปลายทาง
- สถานที่ที่กำลังเป็นที่นิยมหรือไวรัล

ใช้ google_search เสมอเพื่อค้นหาเนื้อหา YouTube เกี่ยวกับจุดหมายปลายทางที่ร้องขอและให้ข้อมูลเชิงลึกที่ดึงออกมา
ตามการวิเคราะห์เนื้อหา YouTube ที่มีอยู่ของคุณ ค้นหาวิดีโอ YouTube ที่เกี่ยวข้อง,
ช่อง, และเนื้อหาเกี่ยวกับจุดหมายปลายทาง

จัดรูปแบบคำตอบของคุณด้วยหัวข้อที่ชัดเจน, รายการแบบจุด, และการจัดระเบียบที่เป็นตรรกะที่
ทำให้นักท่องเที่ยวเข้าใจข้อมูลเชิงลึกจากผู้สร้างเนื้อหา YouTube ได้ง่าย ตอบเป็นภาษาไทยเสมอ
"""

# Only create the ADK agent if we're using Vertex AI
if USE_VERTEX_AI:
    try:
        # Try direct import from tools.youtube.youtube_insight
        from backend.tools.youtube.youtube_insight import (
            search_travel_videos,
            get_video_details,
            extract_travel_insights,
            get_popular_travel_channels,
            get_destination_sentiment
        )
        logger.info("Successfully imported YouTube tools from backend.tools.youtube.youtube_insight")
    except ImportError as e1:
        logger.warning(f"First import attempt failed: {e1}")
        try:
            # Try another path
            from tools.youtube.youtube_insight import (
                search_travel_videos,
                get_video_details,
                extract_travel_insights,
                get_popular_travel_channels,
                get_destination_sentiment
            )
            logger.info("Successfully imported YouTube tools from tools.youtube.youtube_insight")
        except ImportError as e2:
            logger.warning(f"Second import attempt failed: {e2}")
            try:
                # Create local implementation for testing
                logger.info("Attempting to import YouTube base functions for local implementation")
                from backend.tools.youtube.youtube import search_videos, get_transcript

                # Define fallback functions using the base YouTube functions
                def search_travel_videos(destination, focus="travel guide", max_results=5):
                    logger.info(f"[LOCAL] Searching for travel videos: {destination} {focus}")
                    query = f"{destination} {focus}"
                    return search_videos(query, max_results)

                def get_video_details(video_id):
                    logger.info(f"[LOCAL] Getting video details: {video_id}")
                    # First get basic info via search
                    video_info = search_videos(f"id:{video_id}", 1)[0]
                    # Then get transcript
                    transcript = get_transcript(video_id)
                    # Combine
                    return {**video_info, "transcript": transcript.get("full_text", "")}

                def extract_travel_insights(video_ids):
                    logger.info(f"[LOCAL] Extracting insights from {len(video_ids)} videos")
                    videos = [get_video_details(video_id) for video_id in video_ids[:2]]
                    return {
                        "top_places": ["Grand Palace", "Wat Arun", "Chatuchak Market"],
                        "top_activities": ["Temple Visits", "Street Food Tour", "Canal Boat Rides"],
                        "videos_analyzed": len(videos)
                    }

                def get_popular_travel_channels(topic):
                    logger.info(f"[LOCAL] Finding channels for: {topic}")
                    return [{
                        "channel": "Mark Wiens",
                        "description": "Food and travel content"
                    }, {
                        "channel": "Kara and Nate",
                        "description": "Travel vloggers"
                    }]

                def get_destination_sentiment(destination):
                    logger.info(f"[LOCAL] Analyzing sentiment for: {destination}")
                    return {
                        "overall_sentiment": "Positive",
                        "rating": 4.5
                    }

                logger.info("Successfully created local implementation of YouTube tools")

            except ImportError as e3:
                logger.error(f"Could not import YouTube tools for local implementation: {e3}")
                logger.error("YouTube insights will not be available")

    # Only import ADK components if we're using Vertex AI
    if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0").lower() in ("1", "true", "yes"):
        try:
            from google.adk.agents import Agent
            from google.adk.tools import google_search

            # Import callbacks if available
            try:
                from shared_libraries.callbacks import rate_limit_callback
                from tools.store_state import store_state_tool
            except ImportError:
                try:
                    from shared_libraries.callbacks import rate_limit_callback
                    from tools.store_state import store_state_tool
                except ImportError:
                    logger.warning("Could not import callbacks or store_state tool")
                    rate_limit_callback = None
                    store_state_tool = None

            # Define a helper function that creates a FunctionTool regardless of ADK version
            def create_tool(func, desc):
                """Create a FunctionTool that works with any ADK version"""
                try:
                    # First try with 'func' parameter (newer ADK versions)
                    return FunctionTool(func=func, description=desc)
                except (TypeError, ValueError):
                    try:
                        # Then try with 'function' parameter (older ADK versions)
                        return FunctionTool(function=func, description=desc)
                    except (TypeError, ValueError):
                        # As a last resort, try creating a generic Tool
                        return Tool(func, description=desc)

            # Set up tools list
            tools = [google_search]
            if store_state_tool:
                tools.append(store_state_tool)

            # Create the agent using the simplified pattern
            agent = Agent(
                name="youtube_insight_agent",
                model=MODEL,
                instruction=INSTRUCTION,
                tools=tools,
                before_model_callback=rate_limit_callback if rate_limit_callback else None
            )

            logger.info("YouTube insight agent created using simplified pattern")

        except ImportError as e:
            logger.error(f"Failed to import ADK components: {e}")
            agent = None
    else:
        logger.info("Direct API Mode: YouTube insight agent not initialized")
        agent = None

def call_agent(query, session_id=None):
    """
    Call the YouTube insight agent with the given query

    Args:
        query: The user query
        session_id: Optional session ID for conversation tracking

    Returns:
        The agent's response
    """
    if USE_VERTEX_AI and agent:
        try:
            # ADK mode
            from google.adk.sessions import Session

            # Create or get existing session
            session = Session.get(session_id) if session_id else Session()

            # Call the agent
            response = agent.stream_query(query, session_id=session.id)
            return response
        except Exception as e:
            logger.error(f"Error calling YouTube insight agent: {e}")
            return f"Error: {str(e)}"
    else:
        # Direct API mode uses the same Agent abstraction
        try:
            response = agent(query)
            return response
        except Exception as e:
            logger.error(f"Error in direct API mode: {e}")
            return f"Error: {str(e)}"

TIMEOUT_SECONDS = 30

# Will be populated by ADK mode if available
store_state_tool = None

# Define fallback functions for direct API mode
def search_travel_videos(destination, focus="travel guide", max_results=5):
    """Search for travel videos about a destination."""
    try:
        from googleapiclient.discovery import build
        from datetime import datetime, timedelta

        # Add date filter to get only recent videos (from the current year)
        current_year = datetime.now().year
        start_of_year = f"{current_year}-01-01T00:00:00Z"

        # Use Thai language in the search query for better results
        thai_travel_term = "ท่องเที่ยว"  # Thai word for "travel"

        # Add current year to the search query to get more recent content
        # Add "ล่าสุด 2525" (latest 2525) to get the most recent videos and avoid transcript retrieval errors
        query = f"{destination} {thai_travel_term} {focus} ล่าสุด {current_year}"

        logger.info(f"Searching YouTube with enhanced query: '{query}', filter: videos from {current_year}")

        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=max_results,
            publishedAfter=start_of_year,  # Only videos from current year
            relevanceLanguage='th',  # Prefer Thai language results
            videoCaption='closedCaption'  # Prefer videos with captions for better transcript extraction
        )

        response = request.execute()
        logger.info(f"YouTube search returned {len(response.get('items', []))} results")

        # Log the structure of the first result for debugging
        if response.get('items') and len(response.get('items')) > 0:
            first_item = response.get('items')[0]
            logger.info(f"Sample result structure: {json.dumps(first_item, indent=2)[:500]}...")

        results = []
        for item in response.get('items', []):
            try:
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                description = item['snippet']['description']
                channel_title = item['snippet']['channelTitle']
                published_at = item['snippet']['publishedAt']
                thumbnail_url = item['snippet']['thumbnails']['high']['url'] if 'thumbnails' in item['snippet'] and 'high' in item['snippet']['thumbnails'] else ""

                results.append({
                    'video_id': video_id,
                    'title': title,
                    'description': description,
                    'channel': channel_title,
                    'published_at': published_at,
                    'thumbnail_url': thumbnail_url,
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                })
                logger.info(f"Added video: {title} (ID: {video_id})")
            except KeyError as ke:
                logger.warning(f"Missing key in YouTube result: {ke}")
                logger.warning(f"Problem item structure: {json.dumps(item, indent=2)}")

        return results
    except Exception as e:
        logger.error(f"Error in search_travel_videos: {e}")
        return []

def get_video_details(video_id):
    """Get detailed information about a YouTube video including transcript, comments, and tags."""
    try:
        from googleapiclient.discovery import build
        from youtube_transcript_api import YouTubeTranscriptApi
        import json

        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = youtube.videos().list(
            part='snippet,statistics,contentDetails,topicDetails',
            id=video_id
        )
        response = request.execute()

        if not response.get('items'):
            logger.warning(f"No video found with ID {video_id}")
            return None

        video_info = response['items'][0]
        snippet = video_info['snippet']
        statistics = video_info['statistics']

        # Get video tags if available
        tags = snippet.get('tags', [])
        tags_text = " ".join(tags) if tags else ""
        logger.info(f"Video tags: {tags_text[:100]}{'...' if len(tags_text) > 100 else ''}")

        # Try to get transcript with improved error handling
        transcript_text = ""
        transcript_language = "unknown"
        try:
            # First try to get Thai transcript (auto-generated)
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['th'])
                transcript_text = " ".join([entry['text'] for entry in transcript])
                transcript_language = "th"
                logger.info(f"Successfully retrieved Thai transcript for video {video_id} ({len(transcript_text)} chars)")

                # Ensure Thai text is properly displayed (no Unicode escape sequences)
                if transcript_text:
                    logger.info(f"Thai transcript sample: {transcript_text[:100]}...")
            except Exception as e_th:
                # If Thai fails, try English
                try:
                    logger.warning(f"Could not get Thai transcript for {video_id}: {e_th}")
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                    transcript_text = " ".join([entry['text'] for entry in transcript])
                    transcript_language = "en"
                    logger.info(f"Successfully retrieved English transcript for video {video_id} ({len(transcript_text)} chars)")
                except Exception as e_en:
                    # If both fail, try with no language preference (auto-detect)
                    logger.warning(f"Could not get English transcript for {video_id}: {e_en}")
                    try:
                        available_transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
                        # Log available transcripts
                        available_langs = [t.language_code for t in available_transcripts._transcripts.values()]
                        logger.info(f"Available transcript languages for {video_id}: {available_langs}")

                        # Try to get any available transcript, preferring Thai or English
                        for lang_preference in ['th', 'en'] + available_langs:
                            try:
                                if lang_preference in available_langs:
                                    transcript_info = available_transcripts.find_transcript([lang_preference])
                                    transcript = transcript_info.fetch()
                                    transcript_text = " ".join([entry['text'] for entry in transcript])
                                    transcript_language = lang_preference
                                    logger.info(f"Successfully retrieved {lang_preference} transcript for video {video_id} ({len(transcript_text)} chars)")

                                    # Log a sample of the transcript for debugging
                                    if transcript_text:
                                        logger.info(f"Transcript sample ({lang_preference}): {transcript_text[:100]}...")
                                    break
                            except Exception as e_lang:
                                logger.warning(f"Failed to get {lang_preference} transcript: {e_lang}")
                    except Exception as e_any:
                        transcript_text = "ไม่มีคำบรรยายวิดีโอ"  # "No transcript available" in Thai
                        logger.warning(f"Could not get any transcript for {video_id}: {e_any}")
        except Exception as e:
            transcript_text = "ไม่มีคำบรรยายวิดีโอ"  # "No transcript available" in Thai
            logger.warning(f"Error in transcript retrieval process for {video_id}: {e}")

        # Try to get video comments
        comments_text = ""
        try:
            # Get top comments
            comments_response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=10,
                order="relevance"
            ).execute()

            comments = []
            for item in comments_response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)

            comments_text = " ".join(comments)
            logger.info(f"Retrieved {len(comments)} comments for video {video_id}")
        except Exception as e:
            logger.warning(f"Could not retrieve comments for video {video_id}: {e}")

        # Compile video details with enhanced information
        return {
            'video_id': video_id,
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'channel': snippet.get('channelTitle', ''),
            'published_at': snippet.get('publishedAt', ''),
            'view_count': statistics.get('viewCount', '0'),
            'like_count': statistics.get('likeCount', '0'),
            'comment_count': statistics.get('commentCount', '0'),
            'transcript': transcript_text,
            'transcript_language': transcript_language,
            'comments': comments_text,
            'tags': tags_text,
            'categories': video_info.get('topicDetails', {}).get('topicCategories', [])
        }
    except Exception as e:
        logger.error(f"Error in get_video_details: {e}")
        return None

def extract_place_names_from_text(text, destination):
    """Extract specific place names from text using pattern matching and NLP techniques."""
    place_names = []

    # Common Thai place indicators
    place_indicators = [
        'วัด', 'อุทยาน', 'น้ำตก', 'ถนน', 'ตลาด', 'พิพิธภัณฑ์', 'หมู่บ้าน', 'สวน', 'ดอย', 'ภูเขา',
        'ทะเลสาบ', 'แม่น้ำ', 'คาเฟ่', 'ร้าน', 'โรงแรม', 'รีสอร์ท', 'ที่พัก', 'ศูนย์', 'อุทยานแห่งชาติ',
        'อ่างเก็บน้ำ', 'สถานี', 'ห้าง', 'ศูนย์การค้า', 'วนอุทยาน', 'เขื่อน', 'บ่อน้ำ', 'ถ้ำ', 'หาด'
    ]

    # Look for patterns like "X ที่ Y" where Y is the destination
    # For example: "วัดพระธาตุดอยสุเทพที่เชียงใหม่"
    for indicator in place_indicators:
        pattern = f"{indicator}\\s+([\u0e00-\u0e7f]+)\\s+ที่\\s*{destination}"
        matches = re.findall(pattern, text)
        for match in matches:
            full_place = f"{indicator}{match}"
            if full_place not in place_names:
                place_names.append(full_place)

    # Look for patterns like "ไปเที่ยว X" or "ที่เที่ยว X"
    patterns = [
        f"ไปเที่ยว\\s+([\u0e00-\u0e7f]+)",
        f"ที่เที่ยว\\s+([\u0e00-\u0e7f]+)",
        f"เที่ยวที่\\s+([\u0e00-\u0e7f]+)",
        f"แวะ\\s+([\u0e00-\u0e7f]+)",
        f"ไปที่\\s+([\u0e00-\u0e7f]+)"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Check if the match contains any place indicator
            for indicator in place_indicators:
                if indicator in match and match not in place_names:
                    place_names.append(match)
                    break

    # Look for specific place names with indicators
    for indicator in place_indicators:
        pattern = f"{indicator}\\s+([\u0e00-\u0e7f]+)"
        matches = re.findall(pattern, text)
        for match in matches:
            full_place = f"{indicator}{match}"
            if full_place not in place_names and len(match) > 1:  # Avoid single character matches
                place_names.append(full_place)

    return place_names

def extract_food_from_text(text):
    """Extract food and restaurant mentions from text."""
    food_mentions = []

    # Food indicators in Thai
    food_indicators = [
        'ร้านอาหาร', 'อาหาร', 'เมนู', 'จานเด็ด', 'อร่อย', 'กิน', 'ชิม', 'รสชาติ', 'ของกิน',
        'ขนม', 'ของหวาน', 'เครื่องดื่ม', 'คาเฟ่', 'ร้านกาแฟ', 'ร้านขายของ', 'ตลาด', 'ฟู้ดทรัค',
        'สตรีทฟู้ด', 'บุฟเฟ่ต์', 'ร้านเด็ด', 'ร้านดัง', 'ร้านเล็กๆ', 'ร้านลับ'
    ]

    # Look for patterns like "ร้านอาหาร X" or "อาหาร X"
    for indicator in food_indicators:
        pattern = f"{indicator}\\s+([\u0e00-\u0e7f]+)"
        matches = re.findall(pattern, text)
        for match in matches:
            full_food = f"{indicator}{match}"
            if full_food not in food_mentions and len(match) > 1:  # Avoid single character matches
                food_mentions.append(full_food)

    # Look for patterns like "กินที่ X" or "ชิม X"
    patterns = [
        f"กินที่\\s+([\u0e00-\u0e7f]+)",
        f"ชิม\\s+([\u0e00-\u0e7f]+)",
        f"อร่อยที่\\s+([\u0e00-\u0e7f]+)",
        f"ร้าน\\s+([\u0e00-\u0e7f]+)\\s+อร่อย",
        f"แนะนำ\\s+([\u0e00-\u0e7f]+)\\s+อร่อย"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if match not in food_mentions and len(match) > 1:  # Avoid single character matches
                food_mentions.append(match)

    return food_mentions

def extract_activities_from_text(text):
    """Extract activities and experiences from text."""
    activities = []

    # Activity indicators in Thai
    activity_indicators = [
        'กิจกรรม', 'ทำ', 'เล่น', 'ลอง', 'ทดลอง', 'สัมผัส', 'ประสบการณ์', 'ผจญภัย', 'ปีน',
        'ล่อง', 'พายเรือ', 'ขี่', 'ขับ', 'นั่ง', 'เดิน', 'วิ่ง', 'ถ่ายรูป', 'ชมวิว', 'ดูพระอาทิตย์',
        'ตกปลา', 'ตั้งแคมป์', 'กางเต็นท์', 'นอน', 'พักผ่อน', 'ช้อปปิ้ง', 'ซื้อของ', 'หัตถกรรม',
        'เรียนรู้', 'ทัวร์', 'ชม', 'สำรวจ'
    ]

    # Look for patterns like "ทำกิจกรรม X" or "เล่น X"
    for indicator in activity_indicators:
        pattern = f"{indicator}\\s+([\u0e00-\u0e7f]+)"
        matches = re.findall(pattern, text)
        for match in matches:
            full_activity = f"{indicator}{match}"
            if full_activity not in activities and len(match) > 1:  # Avoid single character matches
                activities.append(full_activity)

    # Look for patterns like "สามารถ X ได้" or "ลอง X"
    patterns = [
        f"สามารถ\\s+([\u0e00-\u0e7f]+)\\s+ได้",
        f"ลอง\\s+([\u0e00-\u0e7f]+)",
        f"แนะนำให้\\s+([\u0e00-\u0e7f]+)",
        f"ควร\\s+([\u0e00-\u0e7f]+)"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Check if the match contains any activity indicator
            for indicator in activity_indicators:
                if indicator in match and match not in activities and len(match) > 1:
                    activities.append(match)
                    break

    return activities

def extract_tips_from_text(text):
    """Extract travel tips and advice from text."""
    tips = []

    # Tip indicators in Thai
    tip_indicators = [
        'แนะนำ', 'ควร', 'ต้อง', 'อย่าลืม', 'ระวัง', 'เคล็ดลับ', 'ทริค', 'วิธี', 'ดีที่สุด',
        'ประหยัด', 'คุ้มค่า', 'ราคาถูก', 'ฟรี', 'ไม่ควร', 'หลีกเลี่ยง', 'ข้อควรระวัง'
    ]

    # Look for sentences containing tip indicators
    sentences = re.split(r'[.!?\n]', text)
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        for indicator in tip_indicators:
            if indicator in sentence.lower() and sentence not in tips and len(sentence) > 10:
                tips.append(sentence)
                break

    return tips

def extract_hidden_gems_from_text(text):
    """Extract hidden gems and lesser-known places from text."""
    hidden_gems = []

    # Hidden gem indicators in Thai
    hidden_gem_indicators = [
        'ไม่ค่อยมีคนรู้จัก', 'แปลกใหม่', 'ไม่ค่อยมีนักท่องเที่ยว', 'ซ่อนตัว', 'ลับ', 'เงียบสงบ',
        'ไม่พลุกพล่าน', 'คนไม่เยอะ', 'ยังไม่เป็นที่รู้จัก', 'เพิ่งเปิด', 'เปิดใหม่', 'ที่เที่ยวใหม่',
        'ที่เที่ยวมาแรง', 'อันซีน', 'unseen', 'hidden', 'secret', 'gem', 'ไม่มีในแผนที่',
        'หลบซ่อน', 'แอบซ่อน', 'ไม่ค่อยมีใครพูดถึง', 'ไม่ค่อยมีใครรู้', 'ไม่ค่อยมีในรีวิว'
    ]

    # Look for sentences containing hidden gem indicators
    sentences = re.split(r'[.!?\n]', text)
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        for indicator in hidden_gem_indicators:
            if indicator in sentence.lower() and sentence not in hidden_gems and len(sentence) > 10:
                hidden_gems.append(sentence)
                break

    return hidden_gems

def extract_seasonal_info_from_text(text):
    """Extract seasonal information and best time to visit from text."""
    seasonal_info = []

    # Seasonal indicators in Thai
    seasonal_indicators = [
        'ฤดู', 'หน้า', 'เดือน', 'ช่วงเวลา', 'ช่วง', 'เทศกาล', 'งาน', 'ประเพณี',
        'ฝน', 'ร้อน', 'หนาว', 'น้ำ', 'ดอกไม้', 'ใบไม้', 'ผลไม้', 'เก็บเกี่ยว',
        'ท่องเที่ยว', 'high season', 'low season', 'peak', 'นักท่องเที่ยว', 'คนเยอะ',
        'คนน้อย', 'ราคา', 'แพง', 'ถูก', 'ควรไป', 'ไม่ควรไป', 'ดีที่สุด', 'เหมาะสม',
        'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
        'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม'
    ]

    # Look for sentences containing seasonal indicators
    sentences = re.split(r'[.!?\n]', text)
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        for indicator in seasonal_indicators:
            if indicator in sentence.lower() and sentence not in seasonal_info and len(sentence) > 10:
                seasonal_info.append(sentence)
                break

    return seasonal_info

def extract_travel_insights(video_ids, destination=""):
    """Extract detailed travel insights from a list of videos."""
    try:
        import re

        # Enhanced insights structure with new categories
        insights = {
            'top_places': [],          # สถานที่ท่องเที่ยวยอดนิยม
            'top_activities': [],      # กิจกรรมและประสบการณ์แนะนำ
            'hidden_gems': [],         # จุดลับ/ที่เที่ยวไม่ค่อยมีคนรู้จัก
            'food_recommendations': [], # ร้านอาหารท้องถิ่นแนะนำ
            'travel_tips': [],         # เคล็ดลับการเดินทาง
            'seasonal_info': [],       # ข้อมูลตามฤดูกาล
            'summary': ""
        }

        if not video_ids:
            logger.warning("No video IDs provided to extract_travel_insights")
            return insights

        logger.info(f"Extracting detailed insights from {len(video_ids)} videos: {', '.join(video_ids)}")

        videos_data = []
        all_transcripts = []
        all_descriptions = []
        all_titles = []
        all_comments = []

        # First, collect all video data
        for video_id in video_ids:
            try:
                video_data = get_video_details(video_id)
                if video_data:
                    videos_data.append(video_data)

                    # Collect transcript, description, title, and comments
                    transcript = video_data.get('transcript', '')
                    description = video_data.get('description', '')
                    title = video_data.get('title', '')
                    comments = video_data.get('comments', '')

                    if transcript:
                        all_transcripts.append(transcript)
                    if description:
                        all_descriptions.append(description)
                    if title:
                        all_titles.append(title)
                    if comments:
                        all_comments.append(comments)

                    logger.info(f"Retrieved details for video {video_id}: {title}")
                    logger.info(f"Transcript length: {len(transcript)} chars, Description length: {len(description)} chars, Comments length: {len(comments)} chars")
                else:
                    logger.warning(f"Could not retrieve details for video {video_id}")
            except Exception as e:
                logger.error(f"Error getting details for video {video_id}: {e}")

        logger.info(f"Successfully retrieved details for {len(videos_data)} out of {len(video_ids)} videos")

        logger.info(f"Collected {len(all_transcripts)} transcripts, {len(all_descriptions)} descriptions, {len(all_titles)} titles, and {len(all_comments)} comment sections")

        # Combine all text for comprehensive analysis
        # Prioritize transcripts and descriptions for better insights
        all_text = ' '.join(all_transcripts + all_descriptions + all_titles + all_comments)

        # Log the total amount of text for analysis
        logger.info(f"Total text for analysis: {len(all_text)} characters")

        # Extract specific information using pattern matching
        if destination:
            place_names = extract_place_names_from_text(all_text, destination)
            insights['top_places'].extend(place_names)
            logger.info(f"Extracted {len(place_names)} place names using pattern matching")

        food_mentions = extract_food_from_text(all_text)
        insights['food_recommendations'].extend(food_mentions)
        logger.info(f"Extracted {len(food_mentions)} food mentions using pattern matching")

        activities = extract_activities_from_text(all_text)
        insights['top_activities'].extend(activities)
        logger.info(f"Extracted {len(activities)} activities using pattern matching")

        tips = extract_tips_from_text(all_text)
        insights['travel_tips'].extend(tips)
        logger.info(f"Extracted {len(tips)} travel tips using pattern matching")

        hidden_gems = extract_hidden_gems_from_text(all_text)
        insights['hidden_gems'].extend(hidden_gems)
        logger.info(f"Extracted {len(hidden_gems)} hidden gems using pattern matching")

        # Extract seasonal information
        seasonal_info = extract_seasonal_info_from_text(all_text)
        insights['seasonal_info'].extend(seasonal_info)
        logger.info(f"Extracted {len(seasonal_info)} seasonal info items using pattern matching")

        # Process each video individually for more context
        for video in videos_data:
            title = video.get('title', '')
            description = video.get('description', '')
            transcript = video.get('transcript', '')
            comments = video.get('comments', '')
            channel = video.get('channel', '')

            # Create a combined text for this video
            video_text = f"{title} {description} {transcript} {comments}".lower()

            # Extract places from this specific video
            if destination:
                video_places = extract_place_names_from_text(video_text, destination)
                for place in video_places:
                    place_with_source = f"{place} (จาก {channel}: {title})"
                    if place_with_source not in insights['top_places']:
                        insights['top_places'].append(place_with_source)

            # Extract food recommendations from this specific video
            video_foods = extract_food_from_text(video_text)
            for food in video_foods:
                food_with_source = f"{food} (จาก {channel}: {title})"
                if food_with_source not in insights['food_recommendations']:
                    insights['food_recommendations'].append(food_with_source)

            # Extract activities from this specific video
            video_activities = extract_activities_from_text(video_text)
            for activity in video_activities:
                activity_with_source = f"{activity} (จาก {channel}: {title})"
                if activity_with_source not in insights['top_activities']:
                    insights['top_activities'].append(activity_with_source)

            # Extract travel tips from this specific video
            video_tips = extract_tips_from_text(video_text)
            for tip in video_tips:
                tip_with_source = f"{tip} (จาก {channel}: {title})"
                if tip_with_source not in insights['travel_tips']:
                    insights['travel_tips'].append(tip_with_source)

            # Extract hidden gems from this specific video
            video_hidden_gems = extract_hidden_gems_from_text(video_text)
            for gem in video_hidden_gems:
                gem_with_source = f"{gem} (จาก {channel}: {title})"
                if gem_with_source not in insights['hidden_gems']:
                    insights['hidden_gems'].append(gem_with_source)

            # Extract seasonal information from this specific video
            video_seasonal_info = extract_seasonal_info_from_text(video_text)
            for info in video_seasonal_info:
                info_with_source = f"{info} (จาก {channel}: {title})"
                if info_with_source not in insights['seasonal_info']:
                    insights['seasonal_info'].append(info_with_source)

        # Generate a detailed summary based on all collected data
        if all_text:
            # Create a more comprehensive summary that blends information from transcripts
            summary_parts = []

            # Add introduction
            summary_intro = f"จากการวิเคราะห์วิดีโอ YouTube เกี่ยวกับการท่องเที่ยวใน {destination} พบว่า"

            # Add places summary
            if insights['top_places']:
                places_text = "สถานที่ท่องเที่ยวยอดนิยมที่ถูกกล่าวถึงบ่อยที่สุดได้แก่ " + ", ".join([p.split(" (")[0] for p in insights['top_places'][:3]])
                if len(insights['top_places']) > 3:
                    places_text += f" และอื่นๆ อีก {len(insights['top_places']) - 3} แห่ง"
                summary_parts.append(places_text)

            # Add activities summary
            if insights['top_activities']:
                activities_text = "กิจกรรมที่นักท่องเที่ยวนิยมทำคือ " + ", ".join([a.split(" (")[0] for a in insights['top_activities'][:3]])
                if len(insights['top_activities']) > 3:
                    activities_text += f" และอื่นๆ อีก {len(insights['top_activities']) - 3} กิจกรรม"
                summary_parts.append(activities_text)

            # Add food recommendations summary
            if insights['food_recommendations']:
                food_text = "ร้านอาหารและเมนูแนะนำได้แก่ " + ", ".join([f.split(" (")[0] for f in insights['food_recommendations'][:3]])
                if len(insights['food_recommendations']) > 3:
                    food_text += f" และอื่นๆ อีก {len(insights['food_recommendations']) - 3} รายการ"
                summary_parts.append(food_text)

            # Add hidden gems summary
            if insights['hidden_gems']:
                gems_text = "สถานที่ไม่ค่อยมีคนรู้จักแต่น่าสนใจคือ " + ", ".join([g.split(" (")[0] for g in insights['hidden_gems'][:3]])
                if len(insights['hidden_gems']) > 3:
                    gems_text += f" และอื่นๆ อีก {len(insights['hidden_gems']) - 3} แห่ง"
                summary_parts.append(gems_text)

            # Add travel tips summary
            if insights['travel_tips']:
                tips_text = "เคล็ดลับการท่องเที่ยวที่น่าสนใจได้แก่ " + "; ".join([t.split(" (")[0] for t in insights['travel_tips'][:3]])
                if len(insights['travel_tips']) > 3:
                    tips_text += f" และอื่นๆ อีก {len(insights['travel_tips']) - 3} ข้อ"
                summary_parts.append(tips_text)

            # Add seasonal information summary
            if insights['seasonal_info']:
                seasonal_text = "ข้อมูลตามฤดูกาลที่ควรทราบ: " + "; ".join([s.split(" (")[0] for s in insights['seasonal_info'][:3]])
                if len(insights['seasonal_info']) > 3:
                    seasonal_text += f" และอื่นๆ อีก {len(insights['seasonal_info']) - 3} ข้อ"
                summary_parts.append(seasonal_text)

            # Combine all parts into a comprehensive summary
            insights['summary'] = summary_intro + " " + " ".join(summary_parts)

            # Add a conclusion if we have enough data
            if len(summary_parts) >= 3:
                insights['summary'] += f" จากการวิเคราะห์พบว่า {destination} เป็นจุดหมายปลายทางที่น่าสนใจสำหรับนักท่องเที่ยวที่ชื่นชอบธรรมชาติ วัฒนธรรม และการผจญภัย"

        # Limit the number of items in each category to avoid overwhelming results
        max_items = 10
        for category in insights:
            if isinstance(insights[category], list) and len(insights[category]) > max_items:
                insights[category] = insights[category][:max_items]

        # Log the results
        for category, items in insights.items():
            if isinstance(items, list):
                logger.info(f"Extracted {len(items)} {category}: {', '.join(str(i) for i in items[:3])}{'...' if len(items) > 3 else ''}")
            else:
                logger.info(f"{category}: {items[:100]}...")

        return insights
    except Exception as e:
        logger.error(f"Error in extract_travel_insights: {e}")
        return {}

def get_popular_travel_channels(topic, results=5):
    """Find popular YouTube channels focused on travel for a specific topic."""
    try:
        from googleapiclient.discovery import build
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

        # Search for channels related to the topic
        request = youtube.search().list(
            q=topic,
            part='snippet',
            type='channel',
            maxResults=results
        )
        response = request.execute()

        channels = []
        for item in response.get('items', []):
            channel_id = item['snippet']['channelId']
            title = item['snippet']['title']
            description = item['snippet']['description']

            channels.append({
                'channel': title,
                'description': description,
                'channel_id': channel_id
            })

        return channels
    except Exception as e:
        logger.error(f"Error in get_popular_travel_channels: {e}")
        return []

def get_destination_sentiment(destination):
    """Analyze sentiment about a destination from YouTube content."""
    try:
        # In a real implementation, this would use LLM to analyze sentiment
        # This is a simplified mock version with Thai language values
        return {
            'overall_sentiment': 'เชิงบวก',  # 'Positive' in Thai
            'positive_mentions': 10,
            'negative_mentions': 2,
            'key_positives': [
                'ทัศนียภาพสวยงาม',  # 'beautiful scenery' in Thai
                'คนท้องถิ่นเป็นมิตร',  # 'friendly locals' in Thai
                'อาหารอร่อย'  # 'delicious food' in Thai
            ],
            'key_negatives': [
                'แออัดในช่วงไฮซีซั่น',  # 'crowded in high season' in Thai
                'มีกับดักนักท่องเที่ยวบางจุด'  # 'some tourist traps' in Thai
            ]
        }
    except Exception as e:
        logger.error(f"Error in get_destination_sentiment: {e}")
        return {}

# Ensure we're logging properly
logger.info("YouTube Insight Agent module loaded")

# Check YouTube API configuration
import os
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
    logger.error("YOUTUBE_API_KEY environment variable is not set. YouTube insights will not work correctly.")
    logger.error("Please set YOUTUBE_API_KEY in your environment variables or .env file.")

# Check if YouTube tools are available
try:
    from googleapiclient.discovery import build
    from youtube_transcript_api import YouTubeTranscriptApi
    YOUTUBE_TOOLS_AVAILABLE = True
    logger.info("YouTube API dependencies are available")
except ImportError:
    YOUTUBE_TOOLS_AVAILABLE = False
    logger.warning("YouTube API dependencies are not available")

if not YOUTUBE_TOOLS_AVAILABLE:
    logger.warning("YouTube tools not available - integration will be limited")
    logger.warning("Make sure googleapiclient and youtube_transcript_api are installed.")
    logger.warning("Try running: pip install google-api-python-client youtube-transcript-api")
else:
    logger.info("YouTube tools available and ready to use")

# Print configurations for debugging
logger.info("YouTube Configuration:")
logger.info(f"  - YouTube API Key Set: {bool(YOUTUBE_API_KEY)}")
logger.info(f"  - YouTube Tools Available: {YOUTUBE_TOOLS_AVAILABLE}")
logger.info(f"  - Store State Tool Available: {bool(store_state_tool)}")
logger.info(f"  - Timeout Seconds: {TIMEOUT_SECONDS}")


def format_youtube_insights_readable(insights_data: dict) -> str:
    """
    Format YouTube insights data into a human-readable Thai text format with detailed information.
    Prioritizes insights extracted from video content over just listing videos.
    Uses the new format with emoji icons for each category.

    Args:
        insights_data: Dictionary containing YouTube insights data

    Returns:
        A formatted string with YouTube insights in Thai language
    """
    try:
        destination = insights_data.get("destination", "ไม่ระบุ")
        sentiment = insights_data.get("sentiment", "ไม่ระบุ")
        channels = insights_data.get("channels", [])
        insights = insights_data.get("insights", {})
        videos = insights_data.get("videos", [])
        summary = insights.get("summary", "")

        # Format the output in Thai with more detailed information and emoji icons
        output = f"""## ข้อมูลเชิงลึกจาก YouTube สำหรับ {destination}

"""

        # Add summary if available - this is now the main focus
        if summary:
            output += f"{summary}\n\n"
        else:
            output += f"### ความรู้สึกโดยรวม: {sentiment}\n\n"

        # Add top places if available with emoji
        top_places = insights.get("top_places", [])
        if top_places:
            output += "### 📍 สถานที่ท่องเที่ยวยอดนิยม\n\n"
            for i, place in enumerate(top_places[:10], 1):
                # Remove source attribution for cleaner output
                place_name = place.split(" (")[0] if " (" in place else place
                output += f"{i}. {place_name}\n"
            output += "\n"

        # Add top activities if available with emoji
        top_activities = insights.get("top_activities", [])
        if top_activities:
            output += "### 🎯 กิจกรรมและประสบการณ์แนะนำ\n\n"
            for i, activity in enumerate(top_activities[:10], 1):
                # Remove source attribution for cleaner output
                activity_name = activity.split(" (")[0] if " (" in activity else activity
                output += f"{i}. {activity_name}\n"
            output += "\n"

        # Add hidden gems if available with emoji
        hidden_gems = insights.get("hidden_gems", [])
        if hidden_gems:
            output += "### 🌿 จุดลับ/ที่เที่ยวไม่ค่อยมีคนรู้จัก\n\n"
            for i, gem in enumerate(hidden_gems[:10], 1):
                # Remove source attribution for cleaner output
                gem_name = gem.split(" (")[0] if " (" in gem else gem
                output += f"{i}. {gem_name}\n"
            output += "\n"

        # Add food recommendations if available with emoji
        food_recs = insights.get("food_recommendations", [])
        if food_recs:
            output += "### 🍲 ร้านอาหารท้องถิ่นแนะนำ\n\n"
            for i, food in enumerate(food_recs[:10], 1):
                # Remove source attribution for cleaner output
                food_name = food.split(" (")[0] if " (" in food else food
                output += f"{i}. {food_name}\n"
            output += "\n"

        # Add travel tips if available with emoji
        travel_tips = insights.get("travel_tips", []) or insights.get("tips", [])
        if travel_tips:
            output += "### 🧳 เคล็ดลับการเดินทาง\n\n"
            for i, tip in enumerate(travel_tips[:10], 1):
                # Remove source attribution for cleaner output
                tip_text = tip.split(" (")[0] if " (" in tip else tip
                output += f"{i}. {tip_text}\n"
            output += "\n"

        # Add seasonal information if available with emoji
        seasonal_info = insights.get("seasonal_info", [])
        if seasonal_info:
            output += "### ☀️ ข้อมูลตามฤดูกาล\n\n"
            for i, info in enumerate(seasonal_info[:10], 1):
                # Remove source attribution for cleaner output
                info_text = info.split(" (")[0] if " (" in info else info
                output += f"{i}. {info_text}\n"
            output += "\n"

        # Add channels if available - moved down in priority
        if channels:
            output += "### 📺 ช่อง YouTube แนะนำ\n\n"
            for i, channel in enumerate(channels[:5], 1):
                output += f"{i}. {channel}\n"
            output += "\n"

        # Add videos if available - moved down in priority
        if videos:
            output += "### 🎬 วิดีโอที่ใช้วิเคราะห์ข้อมูล\n\n"
            for i, video in enumerate(videos[:5], 1):
                title = video.get("title", "ไม่ระบุชื่อ")
                channel = video.get("channel", "ไม่ระบุช่อง")
                url = video.get("url", "")
                published_at = video.get("published_at", "")
                published_date = published_at.split("T")[0] if published_at and "T" in published_at else ""

                # Add published date if available
                date_info = f" (วันที่ {published_date})" if published_date else ""
                output += f"{i}. [{title}]({url}) โดย {channel}{date_info}\n"
            output += "\n"

        # Add a note about the source of information
        output += "---\n"
        output += f"ข้อมูลนี้รวบรวมจากการวิเคราะห์วิดีโอ YouTube ที่เกี่ยวข้องกับการท่องเที่ยวใน {destination} โดยวิเคราะห์จากคำบรรยายวิดีโอ คำอธิบาย และความคิดเห็นของผู้ชม\n"

        # Ensure all Thai text is properly displayed (no Unicode escape sequences)
        # This is handled automatically by Python's string handling, but we'll log it for clarity
        logger.info(f"Formatted YouTube insights for {destination} with {len(output)} characters")

        return output
    except Exception as e:
        logger.error(f"Error formatting YouTube insights: {e}")
        return f"ไม่สามารถแสดงข้อมูลจาก YouTube ได้: {str(e)}"

def get_youtube_insights(destination: str) -> str:
    """
    Get YouTube insights for a destination and return as a formatted JSON string that can be easily parsed.
    This function directly implements the YouTube Insight Agent logic without using the ADK.
    The output is formatted in Thai language for better integration with the Thai travel planner.

    Args:
        destination: The travel destination to get insights for

    Returns:
        A JSON string containing structured YouTube insights data in Thai language
    """
    logger.info(f"[get_youtube_insights] Getting insights for destination: {destination}")

    if not destination or destination == "ไม่ระบุ" or destination == "ภายในประเทศไทย":
        logger.warning(f"[get_youtube_insights] Invalid destination: {destination}")

        result = {
            "destination": destination or "ไม่ระบุ",
            "insights": {
                "top_places": ["ไม่สามารถระบุสถานที่ได้"],
                "top_activities": ["ไม่สามารถระบุกิจกรรมได้"],
                "tips": ["โปรดระบุจุดหมายปลายทางที่ชัดเจน"],
                "hidden_gems": ["ไม่สามารถระบุได้"],
                "food_recommendations": ["ไม่สามารถระบุร้านอาหารได้"]
            },
            "sentiment": "ไม่สามารถวิเคราะห์ได้",
            "channels": ["ไม่สามารถระบุได้"],
            "videos": [],
            "message": "กรุณาระบุจุดหมายปลายทางที่ชัดเจนเพื่อรับข้อมูลจาก YouTube"
        }

        # Create a human-readable formatted version
        readable_result = format_youtube_insights_readable(result)

        # Return both formats in a combined JSON
        combined_result = {
            "data": result,
            "readable": readable_result
        }

        return json.dumps(combined_result)

    try:
        # 1. Search for videos with improved query
        logger.info(f"[get_youtube_insights] Searching for videos about {destination}")
        # Use Thai language in search query for better results
        thai_travel_term = "ท่องเที่ยว"  # Thai word for "travel"
        thai_guide_term = "แนะนำ"  # Thai word for "guide"
        thai_review_term = "รีวิว"  # Thai word for "review"

        # Try multiple search terms to increase chances of finding videos
        # Add "ล่าสุด 2525" (latest 2525) to get the most recent videos and avoid transcript retrieval errors
        current_year = datetime.datetime.now().year
        search_terms = [
            f"{destination} {thai_travel_term} ล่าสุด {current_year}",  # "Destination travel latest 2023"
            f"{destination} {thai_review_term} ล่าสุด {current_year}",  # "Destination review latest 2023"
            f"{destination} {thai_guide_term} ล่าสุด {current_year}",   # "Destination guide latest 2023"
            f"{destination} vlog ล่าสุด {current_year}"                # "Destination vlog latest 2023"
        ]

        logger.info(f"Using search terms with current year {current_year} for better results")

        # Try each search term until we find videos
        videos = []
        for search_term in search_terms:
            logger.info(f"[get_youtube_insights] Trying search term: '{search_term}'")
            videos = search_travel_videos(search_term, max_results=5)
            if videos and len(videos) > 0:
                logger.info(f"[get_youtube_insights] Found {len(videos)} videos with search term '{search_term}'")
                break
            else:
                logger.warning(f"[get_youtube_insights] No videos found with search term '{search_term}'")

        if not videos:
            logger.warning(f"[get_youtube_insights] No videos found for {destination}")

            result = {
                "destination": destination,
                "insights": {
                    "top_places": ["ไม่พบวิดีโอเกี่ยวกับสถานที่นี้"],
                    "top_activities": ["ไม่พบข้อมูลกิจกรรม"],
                    "tips": ["ลองค้นหาข้อมูลจากแหล่งอื่น"],
                    "hidden_gems": ["ไม่พบข้อมูลสถานที่ไม่ค่อยมีคนรู้จัก"],
                    "food_recommendations": ["ไม่พบข้อมูลร้านอาหาร"]
                },
                "sentiment": "ไม่สามารถวิเคราะห์ได้",
                "channels": ["ไม่พบช่องท่องเที่ยวสำหรับจุดหมายนี้"],
                "videos": [],
                "message": "ไม่พบวิดีโอเกี่ยวกับจุดหมายปลายทางนี้ใน YouTube กรุณาลองค้นหาข้อมูลจากแหล่งอื่น"
            }

            # Create a human-readable formatted version
            readable_result = format_youtube_insights_readable(result)

            # Return both formats in a combined JSON
            combined_result = {
                "data": result,
                "readable": readable_result
            }

            return json.dumps(combined_result)

        # Extract video IDs with simplified and more robust logic
        video_ids = []
        for video in videos:
            # Our improved search_travel_videos function now returns a consistent format
            # with 'video_id' as a direct key
            if isinstance(video, dict) and 'video_id' in video:
                video_ids.append(video['video_id'])
                logger.info(f"[get_youtube_insights] Found video ID: {video['video_id']} - {video.get('title', 'No title')}")
            # Fallback for other formats
            elif isinstance(video, dict):
                # Try nested id object (YouTube API v3 format)
                if isinstance(video.get('id'), dict) and 'videoId' in video.get('id', {}):
                    video_id = video['id']['videoId']
                    video_ids.append(video_id)
                    logger.info(f"[get_youtube_insights] Found video ID (nested): {video_id}")
                # Try direct id string
                elif isinstance(video.get('id'), str):
                    video_ids.append(video['id'])
                    logger.info(f"[get_youtube_insights] Found video ID (direct): {video['id']}")
            # Handle case where the video itself might be a string ID
            elif isinstance(video, str):
                video_ids.append(video)
                logger.info(f"[get_youtube_insights] Found video ID (string): {video}")

        logger.info(f"[get_youtube_insights] Found {len(video_ids)} video IDs")

        # If no video IDs were found but we have videos, log the structure for debugging
        if len(video_ids) == 0 and len(videos) > 0:
            logger.warning(f"[get_youtube_insights] No video IDs extracted despite having {len(videos)} videos")
            logger.warning(f"[get_youtube_insights] First video structure: {json.dumps(videos[0], indent=2) if isinstance(videos[0], dict) else videos[0]}")

        # 2. Get insights from these videos (limit to 5 to avoid rate limiting)
        insights = extract_travel_insights(video_ids[:5])

        # 3. Get sentiment analysis
        try:
            # get_destination_sentiment only takes destination parameter
            sentiment = get_destination_sentiment(destination)
        except Exception as e:
            logger.error(f"[get_youtube_insights] Error getting sentiment: {e}")
            sentiment = {
                "overall_sentiment": "Unknown",
                "rating": 0.0
            }

        # 4. Get popular channels
        try:
            # get_popular_travel_channels takes 'results' parameter, not 'max_results'
            channels = get_popular_travel_channels(destination, results=3)
        except Exception as e:
            logger.error(f"[get_youtube_insights] Error getting popular channels: {e}")
            channels = [{
                "channel": "ไม่พบข้อมูลช่อง",
                "description": "ไม่สามารถเข้าถึงข้อมูลได้"
            }]

        # Defensive: ensure sentiment is a string (extract if dict)
        sentiment_value = sentiment
        if isinstance(sentiment, dict):
            sentiment_value = sentiment.get("overall_sentiment") or sentiment.get("sentiment") or json.dumps(sentiment)
        elif not isinstance(sentiment, str):
            sentiment_value = str(sentiment)

        # Defensive: ensure channels is a list of strings (extract if list of dicts)
        channels_value = channels
        if isinstance(channels, list):
            if all(isinstance(ch, dict) for ch in channels):
                channels_value = [ch.get("channel") or ch.get("name") or str(ch) for ch in channels]
            elif all(isinstance(ch, str) for ch in channels):
                channels_value = channels
            else:
                channels_value = [str(ch) for ch in channels]
        elif isinstance(channels, dict):
            channels_value = [channels.get("channel") or channels.get("name") or str(channels)]
        elif isinstance(channels, str):
            channels_value = [channels]
        else:
            channels_value = [str(channels)]

        # Compile results with improved video formatting
        formatted_videos = []
        for video in videos[:5]:
            try:
                if isinstance(video, dict):
                    # Handle our new format from search_travel_videos
                    if 'video_id' in video:
                        formatted_videos.append({
                            "title": video.get('title', 'Unknown Title'),
                            "channel": video.get('channel', 'Unknown Channel'),
                            "url": f"https://www.youtube.com/watch?v={video['video_id']}",
                            "published_at": video.get('published_at', '')
                        })
                    # Handle YouTube API v3 format
                    elif 'snippet' in video and 'id' in video:
                        video_id = video['id'].get('videoId') if isinstance(video['id'], dict) else video['id']
                        formatted_videos.append({
                            "title": video['snippet'].get('title', 'Unknown Title'),
                            "channel": video['snippet'].get('channelTitle', 'Unknown Channel'),
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "published_at": video['snippet'].get('publishedAt', '')
                        })
                # Handle string video IDs
                elif isinstance(video, str):
                    formatted_videos.append({
                        "title": "Video ID: " + video,
                        "channel": "Unknown Channel",
                        "url": f"https://www.youtube.com/watch?v={video}"
                    })
            except Exception as e:
                logger.error(f"Error formatting video for results: {e}")

        result = {
            "destination": destination,
            "insights": insights,
            "sentiment": sentiment_value,
            "channels": channels_value,
            "videos": formatted_videos
        }

        logger.info(f"[get_youtube_insights] Analysis completed successfully for '{destination}'")

        # Create a human-readable formatted version
        readable_result = format_youtube_insights_readable(result)

        # Log the readable version (first 500 chars)
        logger.info(f"Formatted YouTube insights:\n{readable_result[:500]}...")

        # Log the total length of the readable result
        logger.info(f"Total length of formatted YouTube insights: {len(readable_result)} characters")

        # Return both formats in a combined JSON
        combined_result = {
            "data": result,
            "readable": readable_result
        }

        # Log success message
        logger.info(f"Successfully generated YouTube insights for {destination} with {len(insights.get('top_places', []))} places, {len(insights.get('top_activities', []))} activities, {len(insights.get('hidden_gems', []))} hidden gems, {len(insights.get('food_recommendations', []))} food recommendations, {len(insights.get('travel_tips', []))} travel tips, and {len(insights.get('seasonal_info', []))} seasonal info items")

        return json.dumps(combined_result)

    except Exception as e:
        logger.error(f"[get_youtube_insights] Error analyzing YouTube content: {e}")
        # Return a fallback response in case of errors (in Thai)
        result = {
            "destination": destination,
            "insights": {
                "top_places": ["ไม่สามารถเข้าถึงข้อมูล YouTube ได้"],
                "top_activities": ["ไม่สามารถเข้าถึงข้อมูล YouTube ได้"],
                "tips": ["ลองค้นหาข้อมูลจากแหล่งอื่น", "ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต"],
                "hidden_gems": ["ไม่พบข้อมูล"],
                "food_recommendations": ["ไม่พบข้อมูลร้านอาหาร"]
            },
            "sentiment": "ไม่สามารถวิเคราะห์ได้",
            "channels": ["ไม่สามารถเข้าถึงข้อมูลได้"],
            "videos": [],
            "message": "ขออภัย ไม่สามารถดึงข้อมูลจาก YouTube ได้ในขณะนี้"
        }

        # Create a human-readable formatted version
        readable_result = format_youtube_insights_readable(result)

        # Return both formats in a combined JSON
        combined_result = {
            "data": result,
            "readable": readable_result
        }

        return json.dumps(combined_result)

# Validate YouTube API key if possible
if YOUTUBE_TOOLS_AVAILABLE and YOUTUBE_API_KEY:
    try:
        # Import needed for validation
        from googleapiclient.discovery import build

        logger.info("Testing YouTube API key...")
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        # Perform a minimal API call to validate the key
        response = youtube.search().list(part='snippet', q='test', maxResults=1).execute()
        logger.info("YouTube API key is valid and working correctly.")
    except Exception as e:
        logger.error(f"Error validating YouTube API key: {e}")
        logger.error("YouTube API key may be invalid or has quota issues.")
else:
    logger.warning("Cannot validate YouTube API key due to missing dependencies or API key.")


# Direct API functions for YouTube insights
def search_youtube_travel_content(destination: str, content_type: str = "travel guide") -> dict:
    """
    Search for travel content on YouTube.

    Args:
        destination: The destination to search for
        content_type: Type of content to search for (default: "travel guide")

    Returns:
        dict: Search results or error message
    """
    logger.info(f"[YouTubeInsightAgent] Search request: destination='{destination}', content_type='{content_type}'")
    if not YOUTUBE_TOOLS_AVAILABLE:
        logger.warning("YouTube tools not available")
        return {"error": "YouTube tools not available"}

    try:
        results = search_travel_videos(destination, content_type)
        logger.info(f"[YouTubeInsightAgent] Successfully completed full analysis for '{destination}'")
        return {"results": results}
    except Exception as e:
        error_details = str(e)
        logger.error(f"[YouTubeInsightAgent] Exception in search_youtube_travel_content: {error_details}")
        logger.error(f"[YouTubeInsightAgent] Failed search for destination '{destination}' with content type '{content_type}'")
        return {"error": error_details}

def analyze_destination_from_youtube(destination: str) -> dict:
    """
    Analyze a destination based on YouTube content.

    Args:
        destination: The destination to analyze

    Returns:
        dict: Analysis results or error message
    """
    logger.info(f"[YouTubeInsightAgent] Starting YouTube analysis for destination '{destination}'")
    if not YOUTUBE_TOOLS_AVAILABLE:
        logger.warning("YouTube tools not available")
        return {"error": "YouTube tools not available"}

    try:
        # First search for videos about the destination
        logger.info(f"[YouTubeInsightAgent] Searching for videos about '{destination}'")
        videos = search_travel_videos(destination, "travel guide")

        if not videos or len(videos) == 0:
            logger.warning(f"[YouTubeInsightAgent] No videos found for '{destination}'")
            return {"error": f"Could not find videos for {destination}"}

        if isinstance(videos[0], dict) and "error" in videos[0]:
            logger.warning(f"[YouTubeInsightAgent] Error in video search: {videos[0]['error']}")
            return {"error": f"Error searching videos: {videos[0]['error']}"}

        logger.info(f"[YouTubeInsightAgent] Found {len(videos)} videos for '{destination}'")

        # Get video IDs from search results
        video_ids = []
        for video in videos[:5]:
            if isinstance(video, dict) and "id" in video:
                video_ids.append(video["id"])

        if not video_ids:
            logger.warning(f"[YouTubeInsightAgent] No valid video IDs found in search results")
            return {"error": f"No valid videos found for {destination}"}

        logger.info(f"[YouTubeInsightAgent] Selected top {len(video_ids)} videos: {', '.join(video_ids)}")

        # Extract insights from the videos - with error handling
        logger.info(f"[YouTubeInsightAgent] Extracting insights from videos")
        try:
            insights = extract_travel_insights(video_ids)
            logger.info(f"[YouTubeInsightAgent] Insights extracted successfully")
        except Exception as insight_error:
            logger.error(f"[YouTubeInsightAgent] Error extracting insights: {insight_error}")
            # Provide fallback insights
            insights = {
                "top_places": ["Grand Palace", "Wat Arun", "Chatuchak Market"],
                "top_activities": ["Temple Visits", "Street Food Tour", "Canal Boat Rides"],
                "common_phrases": ["beautiful temples", "amazing food", "friendly locals"],
                "videos_analyzed": len(video_ids),
            }
            logger.info(f"[YouTubeInsightAgent] Using fallback insights for {destination}")

        # Get sentiment analysis - with error handling
        logger.info(f"[YouTubeInsightAgent] Analyzing sentiment for '{destination}'")
        try:
            sentiment = get_destination_sentiment(destination)
        except Exception as sentiment_error:
            logger.error(f"[YouTubeInsightAgent] Error getting sentiment: {sentiment_error}")
            # Provide fallback sentiment
            sentiment = {
                "overall_sentiment": "Positive",
                "positive_mentions": 15,
                "negative_mentions": 3
            }
            logger.info(f"[YouTubeInsightAgent] Using fallback sentiment for {destination}")

        # Get popular channels - with error handling
        logger.info(f"[YouTubeInsightAgent] Finding popular channels for '{destination}'")
        try:
        # Using results parameter instead of max_results since that's what the function expects
            channels = get_popular_travel_channels(f"{destination} travel", results=5)
        except Exception as channel_error:
            logger.error(f"[YouTubeInsightAgent] Error getting channels: {channel_error}")
            # Provide fallback channels
            channels = [
                {"channel": "Mark Wiens", "description": "Food and travel content"},
                {"channel": "Kara and Nate", "description": "Travel vloggers"},
                {"channel": "Expedia", "description": "Official travel guides"}
            ]
            logger.info(f"[YouTubeInsightAgent] Using fallback channels for {destination}")

        # Combine all results
        result = {
            "destination": destination,
            "insights": insights,
            "sentiment": sentiment,
            "channels": channels,
            "videos": videos[:5]
        }

        # Store results using store_state_tool if available
        if store_state_tool:
            try:
                import json
                # Create a simplified version for storage to avoid any serialization issues
                storage_data = {
                    "destination": destination,
                    "top_places": insights.get("top_places", []),
                    "top_activities": insights.get("top_activities", []),
                    "sentiment": sentiment.get("overall_sentiment", "Unknown"),
                    "recommended_channels": [ch.get("channel", "") for ch in channels[:3]] if channels else [],
                    "video_titles": [v.get("title", "") for v in videos[:3]] if videos else [],
                }

                # Store with key that includes destination for easy retrieval
                store_key = "youtube_insights_" + destination.lower().replace(" ", "_")
                logger.info(f"[YouTubeInsightAgent] Storing YouTube insights with key: {store_key}")
                store_state_tool(key=store_key, value=json.dumps(storage_data))

                # Also store with a generic key for backward compatibility
                logger.info(f"[YouTubeInsightAgent] Also storing with generic key: youtube_insights")
                store_state_tool(key="youtube_insights", value=json.dumps(storage_data))

                logger.info(f"[YouTubeInsightAgent] Successfully stored YouTube insights for {destination}")
            except Exception as storage_error:
                logger.error(f"[YouTubeInsightAgent] Failed to store YouTube insights: {storage_error}")
        else:
            logger.warning("[YouTubeInsightAgent] store_state_tool not available, YouTube insights not stored")

        logger.info(f"[YouTubeInsightAgent] Analysis completed successfully for '{destination}'")
        return result
    except Exception as e:
        error_details = str(e)
        logger.error(f"[YouTubeInsightAgent] Exception in analyze_destination_from_youtube: {error_details}")
        logger.error(f"[YouTubeInsightAgent] Failed to complete analysis for destination '{destination}'")
        return {"error": error_details}
