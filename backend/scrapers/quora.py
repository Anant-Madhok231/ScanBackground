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

import httpx
from bs4 import BeautifulSoup
from typing import List
from models import FootprintResult, QueryInputs, Platform
from scrapers.base_scraper import Scraper


class QuoraScraper(Scraper):
    async def search(self, query_inputs: QueryInputs) -> List[FootprintResult]:
        """Search Quora for user profiles"""
        results = []
        
        for username in query_inputs.usernames:
            try:
                clean_username = username.lstrip('@')
                profile_url = f"https://quora.com/profile/{clean_username}"
                
                async with httpx.AsyncClient(timeout=10.0, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }) as client:
                    response = await client.get(profile_url, follow_redirects=True)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        profile_name = clean_username
                        bio = None
                        posts = []
                        
                        # Look for profile elements (Quora structure may vary)
                        name_elem = soup.find('h1') or soup.find('span', class_='profile_name')
                        if name_elem:
                            profile_name = name_elem.get_text(strip=True)
                        
                        bio_elem = soup.find('div', class_='profile_bio') or soup.find('p', class_='profile_description')
                        if bio_elem:
                            bio = bio_elem.get_text(strip=True)
                        
                        # Look for answers/posts
                        answer_links = soup.find_all('a', href=lambda x: x and '/answer/' in x)
                        for link in answer_links[:10]:
                            answer_url = f"https://quora.com{link.get('href', '')}"
                            answer_text = link.get_text(strip=True)
                            if answer_text:
                                posts.append({
                                    'title': answer_text[:100],
                                    'content': answer_text,
                                    'url': answer_url
                                })
                        
                        result = FootprintResult(
                            platform=Platform.QUORA,
                            username=clean_username,
                            profile_url=profile_url,
                            profile_name=profile_name,
                            bio=bio,
                            posts=posts,
                            comments=[],
                            confidence_score=0.7 if clean_username in query_inputs.usernames else 0.4
                        )
                        results.append(result)
            except Exception:
                continue
        
        return results

