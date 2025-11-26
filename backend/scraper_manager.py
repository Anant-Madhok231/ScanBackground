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

import importlib
import os
import asyncio
from typing import List, Dict
from models import FootprintResult, QueryInputs
from scrapers.base_scraper import Scraper


class ScraperManager:
    def __init__(self):
        self.scrapers: List[Scraper] = []
        self._load_scrapers()
    
    def _load_scrapers(self):
        """Dynamically load all scraper modules"""
        scrapers_dir = os.path.join(os.path.dirname(__file__), 'scrapers')
        
        # List of scraper modules to load
        scraper_modules = [
            'reddit',
            'twitter',
            'instagram',
            'tiktok',
            'youtube',
            'pinterest',
            'tumblr',
            'quora',
            'medium',
            'wordpress',
            'disqus',
            'pastebin',
            'generic_forum',
            'google_search',
            'bing_search',
            'linkedin',
            'github'
        ]
        
        for module_name in scraper_modules:
            try:
                module = importlib.import_module(f'scrapers.{module_name}')
                
                # Find scraper class (class name should be like RedditScraper, TwitterScraper, etc.)
                class_name = ''.join(word.capitalize() for word in module_name.split('_')) + 'Scraper'
                
                if hasattr(module, class_name):
                    scraper_class = getattr(module, class_name)
                    if issubclass(scraper_class, Scraper):
                        scraper_instance = scraper_class()
                        self.scrapers.append(scraper_instance)
            except Exception as e:
                # Silently skip scrapers that fail to load
                print(f"Failed to load scraper {module_name}: {e}")
                continue
    
    async def run_all_scrapers(self, query_inputs: QueryInputs) -> List[FootprintResult]:
        """Run all scrapers in parallel and aggregate results"""
        if not self.scrapers:
            return []
        
        # Run all scrapers in parallel
        tasks = [scraper.search(query_inputs) for scraper in self.scrapers]
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results, filtering out exceptions
        all_results = []
        for results in results_lists:
            if isinstance(results, Exception):
                continue
            if isinstance(results, list):
                all_results.extend(results)
        
        return all_results
    
    def get_scraper_count(self) -> int:
        """Get the number of loaded scrapers"""
        return len(self.scrapers)

