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


class GitHubScraper(Scraper):
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN', '')
        self.base_url = "https://api.github.com"
    
    async def search(self, query_inputs: QueryInputs) -> List[FootprintResult]:
        """Search GitHub for user profiles using GitHub API"""
        results = []
        
        headers = {}
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        
        for username in query_inputs.usernames:
            try:
                clean_username = username.lstrip('@')
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    # Get user profile
                    user_url = f"{self.base_url}/users/{clean_username}"
                    user_response = await client.get(user_url, headers=headers)
                    
                    if user_response.status_code == 200:
                        user_data = user_response.json()
                        
                        # Get user repositories (as "posts")
                        repos_url = user_data.get('repos_url', f"{self.base_url}/users/{clean_username}/repos")
                        repos_params = {
                            'sort': 'updated',
                            'per_page': 10
                        }
                        
                        repos_response = await client.get(repos_url, headers=headers, params=repos_params)
                        posts = []
                        
                        if repos_response.status_code == 200:
                            repos_data = repos_response.json()
                            for repo in repos_data:
                                posts.append({
                                    'title': repo.get('name', ''),
                                    'content': repo.get('description', ''),
                                    'url': repo.get('html_url', ''),
                                    'timestamp': repo.get('updated_at')
                                })
                        
                        # Get user events (activity)
                        events_url = f"{self.base_url}/users/{clean_username}/events/public"
                        events_response = await client.get(events_url, headers=headers, params={'per_page': 10})
                        comments = []
                        
                        if events_response.status_code == 200:
                            events_data = events_response.json()
                            for event in events_data:
                                if event.get('type') in ['IssueCommentEvent', 'PullRequestReviewCommentEvent']:
                                    payload = event.get('payload', {})
                                    comment_data = payload.get('comment', {})
                                    comments.append({
                                        'content': comment_data.get('body', ''),
                                        'url': comment_data.get('html_url', ''),
                                        'timestamp': event.get('created_at')
                                    })
                        
                        result = FootprintResult(
                            platform=Platform.OTHER,
                            username=clean_username,
                            profile_url=user_data.get('html_url', f"https://github.com/{clean_username}"),
                            profile_name=user_data.get('name', clean_username),
                            avatar_url=user_data.get('avatar_url'),
                            bio=user_data.get('bio'),
                            posts=posts,
                            comments=comments,
                            links=[user_data.get('blog')] if user_data.get('blog') else [],
                            confidence_score=0.8 if clean_username in query_inputs.usernames else 0.5
                        )
                        results.append(result)
            except Exception:
                continue
        
        return results

