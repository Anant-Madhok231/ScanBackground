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


class TwitterScraper(Scraper):
    def __init__(self):
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN', '')
        self.base_url = "https://api.twitter.com/2"
    
    async def search(self, query_inputs: QueryInputs) -> List[FootprintResult]:
        """Search Twitter/X for user profiles using Twitter API v2"""
        results = []
        
        if not self.bearer_token:
            return results
        
        headers = {
            'Authorization': f'Bearer {self.bearer_token}'
        }
        
        for username in query_inputs.usernames:
            try:
                clean_username = username.lstrip('@')
                
                # Get user by username
                user_url = f"{self.base_url}/users/by/username/{clean_username}"
                user_params = {
                    'user.fields': 'description,profile_image_url,public_metrics,created_at'
                }
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    user_response = await client.get(user_url, headers=headers, params=user_params)
                    
                    if user_response.status_code == 200:
                        user_data = user_response.json().get('data', {})
                        user_id = user_data.get('id')
                        
                        if user_id:
                            # Get user's tweets
                            tweets_url = f"{self.base_url}/users/{user_id}/tweets"
                            tweets_params = {
                                'max_results': 10,
                                'tweet.fields': 'created_at,public_metrics,text'
                            }
                            
                            tweets_response = await client.get(tweets_url, headers=headers, params=tweets_params)
                            posts = []
                            
                            if tweets_response.status_code == 200:
                                tweets_data = tweets_response.json().get('data', [])
                                for tweet in tweets_data:
                                    posts.append({
                                        'content': tweet.get('text', ''),
                                        'url': f"https://twitter.com/{clean_username}/status/{tweet.get('id')}",
                                        'timestamp': tweet.get('created_at'),
                                        'score': tweet.get('public_metrics', {}).get('like_count', 0)
                                    })
                            
                            result = FootprintResult(
                                platform=Platform.TWITTER,
                                username=clean_username,
                                profile_url=f"https://twitter.com/{clean_username}",
                                profile_name=user_data.get('name', clean_username),
                                avatar_url=user_data.get('profile_image_url'),
                                bio=user_data.get('description'),
                                posts=posts,
                                comments=[],
                                confidence_score=0.8 if clean_username in query_inputs.usernames else 0.5
                            )
                            results.append(result)
            except Exception:
                continue
        
        return results

