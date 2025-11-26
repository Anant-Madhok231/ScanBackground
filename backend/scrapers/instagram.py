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


class InstagramScraper(Scraper):
    def __init__(self):
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
        self.base_url = "https://graph.instagram.com"
    
    async def search(self, query_inputs: QueryInputs) -> List[FootprintResult]:
        """Search Instagram for user profiles using Instagram Basic Display API"""
        results = []
        
        for username in query_inputs.usernames:
            try:
                clean_username = username.lstrip('@')
                profile_url = f"https://instagram.com/{clean_username}"
                
                if self.access_token:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        search_url = f"{self.base_url}/me"
                        params = {
                            'fields': 'id,username,account_type',
                            'access_token': self.access_token
                        }
                        
                        try:
                            response = await client.get(search_url, params=params)
                            if response.status_code == 200:
                                user_data = response.json()
                                # Get user media
                                media_url = f"{self.base_url}/me/media"
                                media_params = {
                                    'fields': 'id,caption,media_type,media_url,permalink,timestamp',
                                    'access_token': self.access_token,
                                    'limit': 10
                                }
                                
                                media_response = await client.get(media_url, params=media_params)
                                posts = []
                                
                                if media_response.status_code == 200:
                                    media_data = media_response.json().get('data', [])
                                    for item in media_data:
                                        posts.append({
                                            'content': item.get('caption', ''),
                                            'url': item.get('permalink', ''),
                                            'timestamp': item.get('timestamp')
                                        })
                                
                                result = FootprintResult(
                                    platform=Platform.INSTAGRAM,
                                    username=user_data.get('username', clean_username),
                                    profile_url=profile_url,
                                    profile_name=user_data.get('username', clean_username),
                                    posts=posts,
                                    comments=[],
                                    confidence_score=0.8 if clean_username in query_inputs.usernames else 0.5
                                )
                                results.append(result)
                        except Exception:
                            pass
                
                if not results:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        response = await client.get(profile_url, follow_redirects=True)
                        
                        if response.status_code == 200:
                            result = FootprintResult(
                                platform=Platform.INSTAGRAM,
                                username=clean_username,
                                profile_url=profile_url,
                                profile_name=clean_username,
                                posts=[],
                                comments=[],
                                confidence_score=0.6 if clean_username in query_inputs.usernames else 0.3
                            )
                            results.append(result)
            except Exception:
                continue
        
        return results

