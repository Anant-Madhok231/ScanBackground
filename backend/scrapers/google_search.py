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
from bs4 import BeautifulSoup
from typing import List
from models import FootprintResult, QueryInputs, Platform
from scrapers.base_scraper import Scraper


class GoogleSearchScraper(Scraper):
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_SEARCH_API_KEY', '')
        self.engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID', '')
    
    async def search(self, query_inputs: QueryInputs) -> List[FootprintResult]:
        """Search Google for digital footprints"""
        results = []
        
        if not self.api_key or not self.engine_id:
            return await self._web_search(query_inputs)
        
        # Build search query
        query_parts = []
        if query_inputs.name:
            query_parts.append(f'"{query_inputs.name}"')
        for username in query_inputs.usernames:
            query_parts.append(f'"{username}"')
        if query_inputs.email:
            query_parts.append(f'"{query_inputs.email}"')
        
        if not query_parts:
            return results
        
        search_query = ' OR '.join(query_parts)
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.api_key,
                'cx': self.engine_id,
                'q': search_query,
                'num': 10
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    
                    for item in items:
                        result = FootprintResult(
                            platform=Platform.SEARCH_RESULT,
                            username=None,
                            profile_url=item.get('link', ''),
                            profile_name=item.get('title', ''),
                            bio=item.get('snippet', ''),
                            posts=[{
                                'title': item.get('title', ''),
                                'content': item.get('snippet', ''),
                                'url': item.get('link', '')
                            }],
                            comments=[],
                            confidence_score=0.5
                        )
                        results.append(result)
        except Exception:
            pass
        
        return results
    
    async def _web_search(self, query_inputs: QueryInputs) -> List[FootprintResult]:
        """Fallback web search when API is not available"""
        results = []
        
        # Build search query
        query_parts = []
        if query_inputs.name:
            query_parts.append(f'"{query_inputs.name}"')
        if query_inputs.email:
            query_parts.append(f'"{query_inputs.email}"')
        
        if not query_parts:
            return results
        
        search_query = ' '.join(query_parts)
        
        try:
            # Use Google search URL
            search_url = "https://www.google.com/search"
            params = {
                'q': search_query,
                'num': 10
            }
            
            async with httpx.AsyncClient(timeout=10.0, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }) as client:
                response = await client.get(search_url, params=params, follow_redirects=True)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find search results
                    search_results = soup.find_all('div', class_='g') or soup.find_all('div', {'data-ved': True})
                    
                    for result in search_results[:10]:
                        try:
                            # Extract title and link
                            title_elem = result.find('h3') or result.find('a')
                            link_elem = result.find('a')
                            
                            if link_elem and title_elem:
                                title = title_elem.get_text(strip=True)
                                link = link_elem.get('href', '')
                                
                                # Clean up Google redirect URLs
                                if link.startswith('/url?q='):
                                    import urllib.parse
                                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)
                                    link = parsed.get('q', [link])[0]
                                
                                # Extract snippet
                                snippet_elem = result.find('span', class_='aCOpRe') or result.find('div', class_='VwiC3b')
                                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                                
                                # Extract images - comprehensive search
                                image_url = None
                                
                                # Method 1: Direct img tag in result
                                img_elem = result.find('img')
                                if img_elem:
                                    for attr in ['src', 'data-src', 'data-lazy-src', 'data-original', 'data-img']:
                                        img_src = img_elem.get(attr)
                                        if img_src and img_src.startswith('http') and not img_src.startswith('data:'):
                                            image_url = img_src
                                            break
                                
                                # Method 2: Look for images in parent/sibling elements
                                if not image_url:
                                    parent = result.find_parent()
                                    if parent:
                                        for img in parent.find_all('img', limit=5):
                                            for attr in ['src', 'data-src', 'data-lazy-src']:
                                                img_src = img.get(attr)
                                                if img_src and img_src.startswith('http') and 'google' not in img_src.lower() and not img_src.startswith('data:'):
                                                    # Prefer external images over Google's own
                                                    image_url = img_src
                                                    break
                                            if image_url:
                                                break
                                
                                if not image_url:
                                    for elem in result.find_all(attrs={'data-img': True}):
                                        img_src = elem.get('data-img')
                                        if img_src and img_src.startswith('http'):
                                            image_url = img_src
                                            break
                                
                                # Clean up image URL
                                if image_url:
                                    if image_url.startswith('//'):
                                        image_url = 'https:' + image_url
                                    elif image_url.startswith('/'):
                                        image_url = None  # Relative URLs not useful
                                    # Filter out Google's own images/icons
                                    if 'google' in image_url.lower() and ('icon' in image_url.lower() or 'logo' in image_url.lower()):
                                        image_url = None
                                
                                # STRICT but practical matching: Require ALL name words to be present
                                confidence = 0.0
                                should_include = False
                                
                                if query_inputs.name:
                                    import re
                                    name_lower = query_inputs.name.lower().strip()
                                    name_parts = [p.strip() for p in name_lower.split() if p.strip() and len(p.strip()) > 1]
                                    title_lower = title.lower()
                                    snippet_lower = snippet.lower()
                                    combined_text = f"{title_lower} {snippet_lower}"
                                    
                                    if len(name_parts) == 0:
                                        confidence = 0.5
                                        should_include = True
                                    # For multi-word names: ALL words must be present
                                    elif len(name_parts) >= 2:
                                        first_name = name_parts[0]
                                        last_name = name_parts[-1]
                                        
                                        # Check if exact full name appears (highest confidence)
                                        if name_lower in combined_text:
                                            confidence = 0.95
                                            should_include = True
                                        # Check if first AND last name both appear (with word boundaries to avoid partial matches)
                                        else:
                                            first_pattern = r'\b' + re.escape(first_name) + r'\b'
                                            last_pattern = r'\b' + re.escape(last_name) + r'\b'
                                            
                                            first_match = re.search(first_pattern, combined_text)
                                            last_match = re.search(last_pattern, combined_text)
                                            
                                            if first_match and last_match:
                                                first_pos = first_match.start()
                                                last_pos = last_match.start()
                                                
                                                # They must be close together (within 40 chars)
                                                if abs(first_pos - last_pos) < 40:
                                                    # Also check ALL middle names if any
                                                    all_parts_present = all(
                                                        re.search(r'\b' + re.escape(part) + r'\b', combined_text) 
                                                        for part in name_parts
                                                    )
                                                    if all_parts_present:
                                                        confidence = 0.85
                                                        should_include = True
                                                    else:
                                                        confidence = 0.0
                                                        should_include = False
                                                else:
                                                    confidence = 0.0
                                                    should_include = False
                                            else:
                                                confidence = 0.0
                                                should_include = False
                                    # Single word name
                                    else:
                                        word_pattern = r'\b' + re.escape(name_parts[0]) + r'\b'
                                        if re.search(word_pattern, combined_text):
                                            confidence = 0.8
                                            should_include = True
                                        else:
                                            confidence = 0.0
                                            should_include = False
                                
                                # Only include if it matches
                                if not should_include:
                                    continue
                                
                                if link and title:
                                    result_obj = FootprintResult(
                                        platform=Platform.SEARCH_RESULT,
                                        username=None,
                                        profile_url=link,
                                        profile_name=title,
                                        avatar_url=image_url,
                                        bio=snippet,
                                        posts=[{
                                            'title': title,
                                            'content': snippet,
                                            'url': link,
                                            'image_url': image_url
                                        }],
                                        comments=[],
                                        links=[link] if link else [],
                                        confidence_score=confidence,
                                        metadata={
                                            'search_query': search_query,
                                            'has_image': image_url is not None
                                        }
                                    )
                                    results.append(result_obj)
                        except Exception:
                            continue
        except Exception:
            pass
        
        return results

