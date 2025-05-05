import os
from typing import Dict, List, Any
from google.adk import LlmAgent
from google.adk.tools import function_tool, search_tool
import aiohttp
import json
from youtube_transcript_api import YouTubeTranscriptApi

class YouTubeVideoAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="YouTubeVideoAgent",
            model="gemini-1.5-flash",
            system_prompt="""คุณเป็นผู้เชี่ยวชาญด้านการค้นหาและคัดเลือกวิดีโอ YouTube ที่เกี่ยวข้องกับการเดินทาง 
            มีหน้าที่ค้นหาและแนะนำวิดีโอที่มีประโยชน์สำหรับการวางแผนการเดินทาง
            
            คุณต้อง:
            1. ค้นหาวิดีโอที่เกี่ยวข้องกับจุดหมายปลายทาง
            2. คัดเลือกวิดีโอที่มีเนื้อหาคุณภาพและข้อมูลที่เป็นประโยชน์
            3. พิจารณา view count, likes, และความน่าเชื่อถือของช่อง
            4. เลือกวิดีโอที่หลากหลาย (travel guide, food review, local tips)
            5. สรุปเนื้อหาสำคัญของแต่ละวิดีโอ
            6. จัดหมวดหมู่วิดีโอตามประเภทเนื้อหา"""
        )
        
        # Add YouTube search tool
        self.add_tool(self._create_youtube_search_tool())
        
        # Add transcript extraction tool
        self.add_tool(self._create_transcript_tool())
    
    def _create_youtube_search_tool(self):
        @function_tool
        async def search_youtube_videos(
            query: str,
            max_results: int = 10,
            order: str = "relevance"
        ) -> Dict:
            """Search for YouTube videos"""
            # Simulated YouTube search results
            # In production, use actual YouTube Data API
            videos = [
                {
                    "id": "video1",
                    "title": f"{query} - Complete Travel Guide 2024",
                    "description": f"Comprehensive guide to {query} covering top attractions, food, and culture.",
                    "thumbnail": f"https://i.ytimg.com/vi/video1/maxresdefault.jpg",
                    "embedUrl": "https://www.youtube.com/embed/video1",
                    "duration": "15:30",
                    "viewCount": "250K",
                    "likeCount": "8.5K",
                    "publishedAt": "2024-01-15",
                    "channelTitle": "Travel Insider",
                    "channelId": "channel1",
                    "tags": ["travel", "guide", query.lower()],
                    "category": "Travel Guide"
                },
                {
                    "id": "video2",
                    "title": f"Street Food Tour in {query} - Must Try Foods!",
                    "description": f"Join us on a street food adventure through {query}. Discover local favorites!",
                    "thumbnail": f"https://i.ytimg.com/vi/video2/maxresdefault.jpg",
                    "embedUrl": "https://www.youtube.com/embed/video2",
                    "duration": "12:45",
                    "viewCount": "180K",
                    "likeCount": "6.2K",
                    "publishedAt": "2024-02-01",
                    "channelTitle": "Food Rangers",
                    "channelId": "channel2",
                    "tags": ["food", "street food", query.lower()],
                    "category": "Food & Cuisine"
                },
                {
                    "id": "video3",
                    "title": f"Top 10 Things to Do in {query} - Local's Guide",
                    "description": f"A local's perspective on the best activities and hidden gems in {query}.",
                    "thumbnail": f"https://i.ytimg.com/vi/video3/maxresdefault.jpg",
                    "embedUrl": "https://www.youtube.com/embed/video3",
                    "duration": "18:20",
                    "viewCount": "320K",
                    "likeCount": "12K",
                    "publishedAt": "2023-11-20",
                    "channelTitle": "Local Wanderer",
                    "channelId": "channel3",
                    "tags": ["activities", "things to do", query.lower()],
                    "category": "Activities & Attractions"
                },
                {
                    "id": "video4",
                    "title": f"{query} Budget Travel Tips - Save Money!",
                    "description": f"How to travel {query} on a budget. Money-saving tips and tricks.",
                    "thumbnail": f"https://i.ytimg.com/vi/video4/maxresdefault.jpg",
                    "embedUrl": "https://www.youtube.com/embed/video4",
                    "duration": "10:15",
                    "viewCount": "95K",
                    "likeCount": "4.1K",
                    "publishedAt": "2024-03-01",
                    "channelTitle": "Budget Backpacker",
                    "channelId": "channel4",
                    "tags": ["budget", "travel tips", query.lower()],
                    "category": "Budget Travel"
                },
                {
                    "id": "video5",
                    "title": f"{query} Hidden Gems - Off the Beaten Path",
                    "description": f"Discover lesser-known attractions and secret spots in {query}.",
                    "thumbnail": f"https://i.ytimg.com/vi/video5/maxresdefault.jpg",
                    "embedUrl": "https://www.youtube.com/embed/video5",
                    "duration": "14:00",
                    "viewCount": "150K",
                    "likeCount": "7.8K",
                    "publishedAt": "2024-01-25",
                    "channelTitle": "Hidden Destinations",
                    "channelId": "channel5",
                    "tags": ["hidden gems", "secret spots", query.lower()],
                    "category": "Hidden Gems"
                }
            ]
            
            return {"videos": videos[:max_results]}
        
        return search_youtube_videos
    
    def _create_transcript_tool(self):
        @function_tool
        async def get_video_transcript(video_id: str) -> Dict:
            """Get transcript of a YouTube video"""
            # Simulated transcript data
            # In production, use actual YouTube Transcript API
            transcript = f"""
            Welcome to our travel guide for this amazing destination. 
            Today we'll explore the top attractions, local food, and cultural experiences.
            
            First stop: The historic city center with its beautiful architecture.
            Don't miss the famous landmark that dates back centuries.
            
            For food lovers, the local market is a must-visit. Try the street food,
            especially the traditional dishes that have been passed down generations.
            
            Pro tip: Visit early morning to avoid crowds and get the best experience.
            The locals are friendly and many speak English, making it easy for tourists.
            
            Transportation is convenient with metro, buses, and affordable taxis.
            Consider getting a tourist pass for unlimited travel.
            
            Best time to visit is during the shoulder season for good weather and fewer tourists.
            """
            
            return {
                "video_id": video_id,
                "transcript": transcript,
                "language": "en",
                "duration": "15:30"
            }
        
        return get_video_transcript
    
    async def run_async(self, context: Dict) -> Dict:
        """Search for relevant YouTube videos based on trip context"""
        destination = context.get("destination")
        preferences = context.get("preferences", {})
        budget = context.get("budget", "medium")
        
        # Create search queries based on context
        search_queries = [
            f"{destination} travel guide 2024",
            f"{destination} things to do",
            f"{destination} food tour",
            f"{destination} budget travel tips",
            f"{destination} hidden gems"
        ]
        
        all_videos = []
        
        # Search for videos using different queries
        for query in search_queries:
            search_results = await self.use_tool(
                "search_youtube_videos",
                query=query,
                max_results=5
            )
            all_videos.extend(search_results.get('videos', []))
        
        # Remove duplicates based on video ID
        unique_videos = {video['id']: video for video in all_videos}.values()
        
        # Get transcripts for top videos (simulated)
        top_videos = list(unique_videos)[:5]
        for video in top_videos:
            try:
                transcript_data = await self.use_tool(
                    "get_video_transcript",
                    video_id=video['id']
                )
                video['transcript_summary'] = self._summarize_transcript(transcript_data['transcript'])
            except:
                video['transcript_summary'] = "Transcript not available"
        
        # Generate recommendations using LLM
        query = f"""
        Based on the following YouTube videos about {destination}, recommend the most useful videos for travelers:
        
        Trip Context:
        - Destination: {destination}
        - Budget: {budget}
        - Preferences: {preferences}
        
        Available Videos:
        {json.dumps(list(unique_videos), indent=2)}
        
        Please provide:
        1. Top 5-7 recommended videos
        2. Why each video is valuable for trip planning
        3. Key takeaways from each video
        4. Categorize videos by content type
        5. Suggest viewing order for maximum benefit
        6. Identify any gaps in video coverage
        
        Consider factors like:
        - Video quality and production value
        - Recency of information
        - Credibility of the channel
        - Relevance to traveler's needs
        - Practical tips vs entertainment value
        
        Format the response to help travelers get the most value from these videos.
        """
        
        response = await self.generate_async(query)
        
        # Organize videos by category
        categorized_videos = self._categorize_videos(list(unique_videos))
        
        return {
            "videos": list(unique_videos)[:10],  # Return top 10 videos
            "recommendations": response,
            "categorized_videos": categorized_videos,
            "video_guide": {
                "viewing_tips": [
                    "Watch travel guides first for overview",
                    "Follow with specific interest videos (food, activities)",
                    "Check video dates for current information",
                    "Read comments for additional tips"
                ],
                "playlist_suggestion": self._create_playlist_suggestion(list(unique_videos)),
                "content_gaps": self._identify_content_gaps(list(unique_videos), destination)
            }
        }
    
    def _summarize_transcript(self, transcript: str) -> str:
        """Summarize video transcript"""
        # Simple summary extraction (in production, use LLM for better summaries)
        sentences = transcript.split('.')
        key_points = []
        
        keywords = ['must', 'tip', 'best', 'don\'t miss', 'recommend', 'important']
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                key_points.append(sentence.strip())
        
        return ' '.join(key_points[:3]) if key_points else "Video covers travel tips and recommendations."
    
    def _categorize_videos(self, videos: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize videos by content type"""
        categories = {
            "Travel Guide": [],
            "Food & Cuisine": [],
            "Activities & Attractions": [],
            "Budget Travel": [],
            "Hidden Gems": [],
            "Culture & History": [],
            "Transportation": [],
            "Accommodation": []
        }
        
        for video in videos:
            category = video.get('category', 'Travel Guide')
            if category in categories:
                categories[category].append(video)
            else:
                categories['Travel Guide'].append(video)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _create_playlist_suggestion(self, videos: List[Dict]) -> List[Dict]:
        """Create suggested viewing order"""
        playlist = []
        
        # Prioritize comprehensive guides first
        guides = [v for v in videos if 'guide' in v['title'].lower()]
        playlist.extend(guides[:2])
        
        # Then specific topics
        food_videos = [v for v in videos if 'food' in v['title'].lower()]
        activity_videos = [v for v in videos if 'things to do' in v['title'].lower()]
        
        playlist.extend(food_videos[:1])
        playlist.extend(activity_videos[:1])
        
        # Add budget and tips videos
        budget_videos = [v for v in videos if 'budget' in v['title'].lower()]
        playlist.extend(budget_videos[:1])
        
        return playlist
    
    def _identify_content_gaps(self, videos: List[Dict], destination: str) -> List[str]:
        """Identify missing content areas"""
        covered_topics = set()
        
        for video in videos:
            title_lower = video['title'].lower()
            if 'food' in title_lower:
                covered_topics.add('food')
            if 'hotel' in title_lower or 'accommodation' in title_lower:
                covered_topics.add('accommodation')
            if 'transport' in title_lower:
                covered_topics.add('transportation')
            if 'budget' in title_lower:
                covered_topics.add('budget')
            if 'culture' in title_lower or 'history' in title_lower:
                covered_topics.add('culture')
            if 'shopping' in title_lower:
                covered_topics.add('shopping')
        
        all_topics = {'food', 'accommodation', 'transportation', 'budget', 'culture', 'shopping', 'safety', 'nightlife'}
        
        missing_topics = all_topics - covered_topics
        
        gaps = []
        for topic in missing_topics:
            gaps.append(f"Limited coverage of {topic} in {destination}")
        
        return gaps
