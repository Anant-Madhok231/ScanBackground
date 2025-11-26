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
import praw
from typing import List
from models import FootprintResult, QueryInputs, Platform
from scrapers.base_scraper import Scraper
import asyncio


class RedditScraper(Scraper):
    def __init__(self):
        self.client_id = os.getenv('REDDIT_CLIENT_ID', '')
        self.client_secret = os.getenv('REDDIT_CLIENT_SECRET', '')
        self.reddit = None
        if self.client_id and self.client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent='FootprintScan/1.0'
                )
            except Exception:
                pass
    
    async def search(self, query_inputs: QueryInputs) -> List[FootprintResult]:
        """Search Reddit for user profiles"""
        results = []
        
        if not self.reddit:
            return results
        
        # Search by usernames
        for username in query_inputs.usernames:
            try:
                user = await asyncio.to_thread(self.reddit.redditor, username)
                
                # Get user info
                posts = []
                comments = []
                
                # Get recent posts
                try:
                    for submission in user.submissions.new(limit=10):
                        posts.append({
                            'title': submission.title,
                            'content': submission.selftext,
                            'url': f"https://reddit.com{submission.permalink}",
                            'timestamp': submission.created_utc,
                            'score': submission.score
                        })
                except Exception:
                    pass
                
                # Get recent comments
                try:
                    for comment in user.comments.new(limit=10):
                        comments.append({
                            'content': comment.body,
                            'url': f"https://reddit.com{comment.permalink}",
                            'timestamp': comment.created_utc,
                            'score': comment.score
                        })
                except Exception:
                    pass
                
                # Get user profile info
                try:
                    user_info = await asyncio.to_thread(lambda: user)
                    bio = None
                    avatar_url = None
                    # Reddit API doesn't expose bio directly, but we can get subreddit karma
                except Exception:
                    pass
                
                result = FootprintResult(
                    platform=Platform.REDDIT,
                    username=username,
                    profile_url=f"https://reddit.com/user/{username}",
                    profile_name=username,
                    bio=None,
                    posts=posts,
                    comments=comments,
                    confidence_score=0.8 if username in query_inputs.usernames else 0.5,
                    metadata={
                        'post_count': len(posts),
                        'comment_count': len(comments)
                    }
                )
                results.append(result)
            except Exception:
                continue
        
        return results

