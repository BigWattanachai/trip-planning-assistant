from google.adk import Agent
from google.adk.tools import google_search, function_tool
from typing import Dict, Any, Optional, List
import logging
import re
import aiohttp
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

logger = logging.getLogger(__name__)

class YouTubeVideoAgent:
    """
    Agent responsible for finding relevant travel videos and extracting information from them.
    """
    
    def __init__(self, model: str = "gemini-1.5-flash"):
        """
        Initialize the YouTubeVideoAgent.
        
        Args:
            model: The Gemini model to use for the agent.
        """
        self.agent = Agent(
            name="YouTube Video Agent",
            model=model,
            tools=[
                google_search(),
                function_tool(self.search_youtube_videos),
                function_tool(self.get_video_transcript)
            ],
            system_prompt="""
            You are an expert YouTube travel video curator who helps travelers find the best and most
            informative videos about their travel destinations.
            
            Focus on providing:
            - High-quality, informative travel videos for specific destinations
            - Videos that cover attractions, accommodation options, local cuisine, and travel tips
            - Content from reputable travel creators and official tourism channels
            - Videos with recent information when available
            - A mix of comprehensive guides and specialized content based on user interests
            
            For each video recommendation, extract and provide:
            - Title of the video
            - Channel name
            - Brief description of what the video covers
            - Key highlights or tips mentioned in the video
            - Why this video would be useful for the traveler
            
            If you have access to video transcripts, use them to extract specific, valuable information
            that would help the traveler plan their trip.
            
            Always aim to recommend videos that provide practical, actionable advice rather than just
            visually appealing content without substance.
            """
        )
    
    async def search_youtube_videos(self, 
                             query: str, 
                             max_results: int = 5) -> Dict[str, Any]:
        """
        Search for YouTube videos based on a query.
        
        Args:
            query: The search query for YouTube videos.
            max_results: Maximum number of results to return.
            
        Returns:
            Dictionary containing YouTube video search results.
        """
        logger.info(f"Searching YouTube videos for: {query}")
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    if response.status != 200:
                        return {"success": False, "error": f"HTTP Error: {response.status}"}
                    
                    html_content = await response.text()
            
            # Parse video information using BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract video IDs using regex (YouTube format)
            video_ids = re.findall(r"watch\?v=(\S{11})", html_content)
            unique_video_ids = list(dict.fromkeys(video_ids))  # Remove duplicates while preserving order
            
            # Limit results
            video_ids = unique_video_ids[:max_results]
            
            # Prepare results
            videos = []
            for video_id in video_ids:
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                videos.append({
                    "video_id": video_id,
                    "url": video_url,
                    "embed_url": f"https://www.youtube.com/embed/{video_id}"
                })
            
            return {
                "success": True,
                "videos": videos,
                "count": len(videos),
                "query": query
            }
        
        except Exception as e:
            logger.error(f"Error searching YouTube videos: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve YouTube videos."
            }
    
    async def get_video_transcript(self, video_id: str, language_code: str = "en") -> Dict[str, Any]:
        """
        Retrieve and return the transcript of a YouTube video.
        
        Args:
            video_id: The YouTube video ID.
            language_code: Preferred language code for the transcript.
            
        Returns:
            Dictionary containing the video transcript and related information.
        """
        logger.info(f"Getting transcript for YouTube video: {video_id}")
        
        try:
            # Get available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get the transcript in the preferred language
            try:
                transcript = transcript_list.find_transcript([language_code])
            except NoTranscriptFound:
                # If preferred language not found, try to get any available transcript and translate
                try:
                    transcript = transcript_list.find_transcript(['en', 'es', 'fr', 'de'])
                    if transcript.language_code != language_code:
                        transcript = transcript.translate(language_code)
                except Exception as e:
                    # Use any available transcript if translation fails
                    transcript = list(transcript_list)[0]
            
            # Get the transcript data
            transcript_data = transcript.fetch()
            
            # Convert to readable text format
            full_text = " ".join([entry['text'] for entry in transcript_data])
            
            # Create timestamps with text chunks for reference
            segments = []
            for entry in transcript_data:
                segments.append({
                    "start": entry['start'],
                    "duration": entry['duration'],
                    "text": entry['text']
                })
            
            return {
                "success": True,
                "video_id": video_id,
                "language": transcript.language_code,
                "transcript": full_text,
                "segments": segments
            }
        
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            return {
                "success": False,
                "video_id": video_id,
                "error": "No transcript available for this video",
                "message": "This video doesn't have subtitles or transcripts enabled."
            }
        
        except Exception as e:
            logger.error(f"Error getting video transcript: {str(e)}")
            return {
                "success": False,
                "video_id": video_id,
                "error": str(e),
                "message": "Failed to retrieve video transcript."
            }
    
    async def find_travel_videos(self, 
                          location: str, 
                          topic: Optional[str] = None,
                          max_results: int = 3,
                          include_transcripts: bool = False) -> Dict[str, Any]:
        """
        Find travel videos for a specific location and topic.
        
        Args:
            location: The destination location.
            topic: Specific topic of interest (e.g., "food", "attractions", "tips").
            max_results: Maximum number of videos to return.
            include_transcripts: Whether to include video transcripts.
            
        Returns:
            Dictionary containing video recommendations and related information.
        """
        logger.info(f"Finding travel videos for {location}")
        
        # Prepare the search query
        query = f"travel guide {location}"
        if topic:
            query += f" {topic}"
        
        # Get initial video recommendations using the agent
        prompt = f"Find the best YouTube travel videos about {location}"
        if topic:
            prompt += f" focusing on {topic}"
        prompt += f". Suggest up to {max_results} high-quality, informative videos that would help travelers plan their trip."
        
        try:
            # Search for videos
            videos_data = await self.search_youtube_videos(query, max_results=max_results)
            
            if not videos_data["success"]:
                return videos_data
            
            videos = videos_data["videos"]
            
            # Get transcripts if requested
            if include_transcripts and videos:
                for i, video in enumerate(videos):
                    video_id = video["video_id"]
                    transcript_data = await self.get_video_transcript(video_id)
                    videos[i]["transcript_available"] = transcript_data["success"]
                    if transcript_data["success"]:
                        videos[i]["transcript"] = transcript_data["transcript"]
            
            # Ask the agent to analyze the videos and provide recommendations
            video_urls = [v["url"] for v in videos]
            video_list = "\n".join([f"{i+1}. {v['url']}" for i, v in enumerate(videos)])
            
            analysis_prompt = f"""
            I've found these travel videos about {location}:
            
            {video_list}
            
            Please analyze these videos and provide a curated recommendation for each, including:
            - What the video covers
            - Why it would be helpful for travelers
            - Key highlights or tips from the video
            
            Format your response as a structured list of recommendations.
            """
            
            analysis = await self.agent.run_async(analysis_prompt)
            
            return {
                "success": True,
                "location": location,
                "topic": topic,
                "videos": videos,
                "analysis": analysis,
                "count": len(videos)
            }
            
        except Exception as e:
            logger.error(f"Error finding travel videos: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve travel video recommendations."
            }
