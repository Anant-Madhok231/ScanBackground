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


class MediumScraper(Scraper):
    async def search(self, query_inputs: QueryInputs) -> List[FootprintResult]:
        """Search Medium for user profiles"""
        results = []
        
        for username in query_inputs.usernames:
            try:
                clean_username = username.lstrip('@')
                profile_url = f"https://medium.com/@{clean_username}"
                
                async with httpx.AsyncClient(timeout=10.0, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }) as client:
                    response = await client.get(profile_url, follow_redirects=True)
                    
                    if response.status_code == 200:
                        # Parse HTML to extract profile info
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        profile_name = clean_username
                        bio = None
                        posts = []
                        
                        # Extract profile info from JSON-LD or meta tags
                        json_ld = soup.find('script', type='application/ld+json')
                        if json_ld:
                            import json
                            try:
                                data = json.loads(json_ld.string)
                                if isinstance(data, dict):
                                    profile_name = data.get('name', clean_username)
                                    bio = data.get('description')
                            except Exception:
                                pass
                        
                        # Look for article links
                        article_links = soup.find_all('a', href=lambda x: x and f'/@{clean_username}/' in x)
                        for link in article_links[:10]:
                            article_url = link.get('href', '')
                            if not article_url.startswith('http'):
                                article_url = f"https://medium.com{article_url}"
                            
                            title_elem = link.find('h2') or link.find('h3')
                            if title_elem:
                                title = title_elem.get_text(strip=True)
                                posts.append({
                                    'title': title,
                                    'content': title,
                                    'url': article_url
                                })
                        
                        result = FootprintResult(
                            platform=Platform.MEDIUM,
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

