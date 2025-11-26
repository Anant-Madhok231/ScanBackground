"""
Copyright (c) 2024 FootprintScan. All Rights Reserved.

This software and associated documentation files (the "Software") are proprietary
and confidential. Unauthorized copying, modification, distribution, or use of
this Software, via any medium, is strictly prohibited without express written
permission from the copyright holder.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
"""

import os
import httpx
from typing import List
from models import FootprintResult, QueryInputs, Platform
from scrapers.base_scraper import Scraper


class YouTubeScraper(Scraper):
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY', '')
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    async def search(self, query_inputs: QueryInputs) -> List[FootprintResult]:
        """Search YouTube for user channels using YouTube Data API v3"""
        results = []
        
        if not self.api_key:
            return results
        
        for username in query_inputs.usernames:
            try:
                clean_username = username.lstrip('@')
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    # Search for channel by username
                    search_url = f"{self.base_url}/search"
                    search_params = {
                        'key': self.api_key,
                        'part': 'snippet',
                        'q': clean_username,
                        'type': 'channel',
                        'maxResults': 1
                    }
                    
                    search_response = await client.get(search_url, params=search_params)
                    
                    if search_response.status_code == 200:
                        search_data = search_response.json()
                        items = search_data.get('items', [])
                        
                        for item in items:
                            channel_id = item['id'].get('channelId')
                            snippet = item.get('snippet', {})
                            
                            if channel_id:
                                # Get channel details
                                channel_url = f"{self.base_url}/channels"
                                channel_params = {
                                    'key': self.api_key,
                                    'part': 'snippet,contentDetails,statistics',
                                    'id': channel_id
                                }
                                
                                channel_response = await client.get(channel_url, params=channel_params)
                                
                                if channel_response.status_code == 200:
                                    channel_data = channel_response.json().get('items', [])
                                    
                                    if channel_data:
                                        channel = channel_data[0]
                                        channel_snippet = channel.get('snippet', {})
                                        
                                        # Get recent videos
                                        uploads_playlist = channel.get('contentDetails', {}).get('relatedPlaylists', {}).get('uploads')
                                        posts = []
                                        
                                        if uploads_playlist:
                                            videos_url = f"{self.base_url}/playlistItems"
                                            videos_params = {
                                                'key': self.api_key,
                                                'part': 'snippet',
                                                'playlistId': uploads_playlist,
                                                'maxResults': 10
                                            }
                                            
                                            videos_response = await client.get(videos_url, params=videos_params)
                                            
                                            if videos_response.status_code == 200:
                                                videos_data = videos_response.json().get('items', [])
                                                for video in videos_data:
                                                    video_snippet = video.get('snippet', {})
                                                    posts.append({
                                                        'title': video_snippet.get('title', ''),
                                                        'content': video_snippet.get('description', ''),
                                                        'url': f"https://youtube.com/watch?v={video_snippet.get('resourceId', {}).get('videoId')}",
                                                        'timestamp': video_snippet.get('publishedAt')
                                                    })
                                        
                                        result = FootprintResult(
                                            platform=Platform.YOUTUBE,
                                            username=clean_username,
                                            profile_url=f"https://youtube.com/@{channel_snippet.get('customUrl', clean_username)}",
                                            profile_name=channel_snippet.get('title', clean_username),
                                            avatar_url=channel_snippet.get('thumbnails', {}).get('high', {}).get('url'),
                                            bio=channel_snippet.get('description'),
                                            posts=posts,
                                            comments=[],
                                            confidence_score=0.8 if clean_username in query_inputs.usernames else 0.5
                                        )
                                        results.append(result)
            except Exception:
                continue
        
        return results

