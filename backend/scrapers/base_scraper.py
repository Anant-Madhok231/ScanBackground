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

from abc import ABC, abstractmethod
from typing import List
from models import FootprintResult, QueryInputs


class Scraper(ABC):
    """Base class for all scrapers"""
    
    @abstractmethod
    async def search(self, query_inputs: QueryInputs) -> List[FootprintResult]:
        """
        Search for digital footprints based on query inputs.
        
        Args:
            query_inputs: QueryInputs object containing name, usernames, email
            
        Returns:
            List of FootprintResult objects
        """
        pass
    
    def get_platform_name(self) -> str:
        """Return the platform name"""
        return self.__class__.__name__.lower().replace('scraper', '')

