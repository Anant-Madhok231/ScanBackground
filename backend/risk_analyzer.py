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

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter
import numpy as np

try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class RiskAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        
        # Toxicity keywords
        self.toxicity_keywords = {
            'insult', 'stupid', 'idiot', 'moron', 'dumb', 'fool', 'loser',
            'hate', 'despise', 'loathe', 'disgusting', 'pathetic', 'worthless'
        }
        
        # Hate speech indicators
        self.hate_keywords = {
            'racist', 'racism', 'sexist', 'sexism', 'homophobic', 'bigot',
            'nazi', 'fascist', 'supremacist', 'discrimination', 'prejudice'
        }
        
        # NSFW indicators
        self.nsfw_keywords = {
            'nsfw', 'explicit', 'adult', 'xxx', 'porn', 'sexual', 'nude',
            'naked', 'erotic', 'lewd', 'vulgar', 'obscene'
        }
        
        # Political intensity keywords
        self.political_keywords = {
            'politics', 'political', 'election', 'vote', 'democrat', 'republican',
            'liberal', 'conservative', 'left', 'right', 'government', 'policy',
            'congress', 'senate', 'president', 'trump', 'biden', 'republic',
            'democracy', 'authoritarian', 'fascism', 'socialism', 'capitalism'
        }
    
    def calculate_toxicity(self, content: str) -> float:
        """Calculate toxicity score"""
        if not content:
            return 0.0
        
        content_lower = content.lower()
        word_count = len(content.split())
        
        if word_count == 0:
            return 0.0
        
        # Count toxicity keywords
        toxicity_count = sum(1 for keyword in self.toxicity_keywords if keyword in content_lower)
        
        # Normalize by word count
        toxicity_score = min(1.0, (toxicity_count / max(word_count, 1)) * 10)
        
        # Check for all caps (shouting)
        if len(content) > 10 and content.isupper():
            toxicity_score = min(1.0, toxicity_score + 0.2)
        
        # Check for excessive punctuation
        if content.count('!') > 3 or content.count('?') > 5:
            toxicity_score = min(1.0, toxicity_score + 0.1)
        
        return float(toxicity_score)
    
    def calculate_hate_speech(self, content: str) -> float:
        """Calculate hate speech probability"""
        if not content:
            return 0.0
        
        content_lower = content.lower()
        word_count = len(content.split())
        
        if word_count == 0:
            return 0.0
        
        # Count hate speech keywords
        hate_count = sum(1 for keyword in self.hate_keywords if keyword in content_lower)
        
        # Normalize by word count
        hate_score = min(1.0, (hate_count / max(word_count, 1)) * 15)
        
        return float(hate_score)
    
    def calculate_nsfw(self, content: str) -> float:
        """Calculate NSFW likelihood"""
        if not content:
            return 0.0
        
        content_lower = content.lower()
        word_count = len(content.split())
        
        if word_count == 0:
            return 0.0
        
        # Count NSFW keywords
        nsfw_count = sum(1 for keyword in self.nsfw_keywords if keyword in content_lower)
        
        # Normalize by word count
        nsfw_score = min(1.0, (nsfw_count / max(word_count, 1)) * 20)
        
        return float(nsfw_score)
    
    def calculate_political_intensity(self, content: str) -> float:
        """Calculate political intensity"""
        if not content:
            return 0.0
        
        content_lower = content.lower()
        word_count = len(content.split())
        
        if word_count == 0:
            return 0.0
        
        # Count political keywords
        political_count = sum(1 for keyword in self.political_keywords if keyword in content_lower)
        
        # Normalize by word count
        political_score = min(1.0, (political_count / max(word_count, 1)) * 5)
        
        return float(political_score)
    
    def calculate_sentiment(self, content: str) -> float:
        """Calculate sentiment score (-1 to 1)"""
        if not content:
            return 0.0
        
        scores = self.sia.polarity_scores(content)
        # Return compound score normalized to -1 to 1
        return float(scores['compound'])
    
    def calculate_volatility(self, posts: List[Dict[str, Any]]) -> float:
        """Calculate posting volatility based on frequency and content variation"""
        if not posts or len(posts) < 2:
            return 0.0
        
        # Extract timestamps
        timestamps = []
        for post in posts:
            if 'timestamp' in post:
                try:
                    if isinstance(post['timestamp'], str):
                        ts = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))
                    else:
                        ts = post['timestamp']
                    timestamps.append(ts)
                except Exception:
                    pass
        
        if len(timestamps) < 2:
            return 0.5  # Default moderate volatility
        
        # Calculate time intervals
        timestamps.sort()
        intervals = []
        for i in range(1, len(timestamps)):
            delta = (timestamps[i] - timestamps[i-1]).total_seconds() / 3600  # hours
            if delta > 0:
                intervals.append(delta)
        
        if not intervals:
            return 0.5
        
        # High volatility = irregular posting patterns
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        if mean_interval == 0:
            return 1.0  # Very frequent posting
        
        coefficient_of_variation = std_interval / mean_interval if mean_interval > 0 else 0
        volatility = min(1.0, coefficient_of_variation)
        
        return float(volatility)
    
    def analyze_risk(self, content: str, posts: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze risk for a single post/comment"""
        toxicity = self.calculate_toxicity(content)
        hate = self.calculate_hate_speech(content)
        nsfw = self.calculate_nsfw(content)
        politics = self.calculate_political_intensity(content)
        sentiment = self.calculate_sentiment(content)
        volatility = self.calculate_volatility(posts)
        
        # Calculate overall risk score
        overall_risk = (0.40 * toxicity + 0.20 * hate + 0.15 * nsfw + 
                       0.15 * politics + 0.10 * volatility) * 100
        
        return {
            'toxicity': toxicity,
            'hate_speech': hate,
            'nsfw': nsfw,
            'political_intensity': politics,
            'sentiment': sentiment,
            'volatility': volatility,
            'overall_risk': overall_risk
        }
    
    def should_flag(self, risk_metrics: Dict[str, float]) -> tuple[bool, List[str]]:
        """Determine if content should be flagged and why"""
        flags = []
        
        if risk_metrics['toxicity'] > 0.5:
            flags.append('High Toxicity')
        
        if risk_metrics['hate_speech'] > 0.3:
            flags.append('Hate Speech')
        
        if risk_metrics['nsfw'] > 0.4:
            flags.append('NSFW Content')
        
        if risk_metrics['political_intensity'] > 0.6:
            flags.append('High Political Intensity')
        
        if risk_metrics['overall_risk'] > 70:
            flags.append('High Overall Risk')
        
        return len(flags) > 0, flags

