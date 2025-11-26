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
from typing import List
from models import FootprintResult, QueryInputs, Platform
from scrapers.base_scraper import Scraper


class PinterestScraper(Scraper):
    async def search(self, query_inputs: QueryInputs) -> List[FootprintResult]:
        """Search Pinterest for user profiles"""
        results = []
        
        for username in query_inputs.usernames:
            try:
                clean_username = username.lstrip('@')
                profile_url = f"https://pinterest.com/{clean_username}"
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(profile_url, follow_redirects=True)
                    
                    if response.status_code == 200:
                        result = FootprintResult(
                            platform=Platform.PINTEREST,
                            username=clean_username,
                            profile_url=profile_url,
                            profile_name=clean_username,
                            posts=[],
                            comments=[],
                            confidence_score=0.7 if clean_username in query_inputs.usernames else 0.4
                        )
                        results.append(result)
            except Exception:
                continue
        
        return results

