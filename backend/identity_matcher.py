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
import difflib
from typing import List, Dict, Optional
from PIL import Image
import imagehash
import httpx
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from collections import Counter
import hashlib

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


class IdentityMatcher:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.avatar_cache: Dict[str, str] = {}
    
    def normalize_username(self, username: str) -> str:
        """Normalize username for comparison"""
        if not username:
            return ""
        # Remove common prefixes/suffixes
        username = username.lower().strip()
        username = re.sub(r'^@', '', username)
        username = re.sub(r'[^a-z0-9_]', '', username)
        return username
    
    def username_similarity(self, username1: str, username2: str) -> float:
        """Calculate username similarity score"""
        norm1 = self.normalize_username(username1)
        norm2 = self.normalize_username(username2)
        
        if not norm1 or not norm2:
            return 0.0
        
        if norm1 == norm2:
            return 1.0
        
        # Use sequence matcher for similarity
        similarity = difflib.SequenceMatcher(None, norm1, norm2).ratio()
        
        # Check for substring matches
        if norm1 in norm2 or norm2 in norm1:
            similarity = max(similarity, 0.8)
        
        return similarity
    
    async def fetch_avatar_hash(self, avatar_url: Optional[str]) -> Optional[str]:
        """Fetch avatar and compute perceptual hash"""
        if not avatar_url:
            return None
        
        # Check cache
        if avatar_url in self.avatar_cache:
            return self.avatar_cache[avatar_url]
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(avatar_url)
                if response.status_code == 200:
                    from io import BytesIO
                    img = Image.open(BytesIO(response.content))
                    # Resize for consistent hashing
                    img = img.resize((256, 256))
                    phash = str(imagehash.phash(img))
                    self.avatar_cache[avatar_url] = phash
                    return phash
        except Exception:
            pass
        
        return None
    
    def avatar_similarity(self, hash1: Optional[str], hash2: Optional[str]) -> float:
        """Compare avatar perceptual hashes"""
        if not hash1 or not hash2:
            return 0.0
        
        if hash1 == hash2:
            return 1.0
        
        try:
            # Calculate hamming distance
            h1 = imagehash.hex_to_hash(hash1)
            h2 = imagehash.hex_to_hash(hash2)
            distance = h1 - h2
            # Normalize to 0-1 (max distance is typically 64 for phash)
            similarity = 1.0 - (distance / 64.0)
            return max(0.0, min(1.0, similarity))
        except Exception:
            return 0.0
    
    def bio_similarity(self, bio1: Optional[str], bio2: Optional[str]) -> float:
        """Calculate bio similarity using embeddings"""
        if not bio1 or not bio2:
            return 0.0
        
        if bio1 == bio2:
            return 1.0
        
        try:
            embeddings = self.embedding_model.encode([bio1, bio2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(max(0.0, min(1.0, similarity)))
        except Exception:
            return 0.0
    
    def extract_ngrams(self, text: str, n: int = 3) -> List[str]:
        """Extract n-grams from text"""
        if not text:
            return []
        
        words = nltk.word_tokenize(text.lower())
        ngrams = []
        for i in range(len(words) - n + 1):
            ngrams.append(' '.join(words[i:i+n]))
        return ngrams
    
    def stylometry_similarity(self, texts1: List[str], texts2: List[str]) -> float:
        """Calculate writing style similarity using n-gram stylometry"""
        if not texts1 or not texts2:
            return 0.0
        
        # Combine all texts
        combined1 = ' '.join(texts1)
        combined2 = ' '.join(texts2)
        
        if not combined1 or not combined2:
            return 0.0
        
        # Extract n-grams
        ngrams1 = self.extract_ngrams(combined1, n=3)
        ngrams2 = self.extract_ngrams(combined2, n=3)
        
        if not ngrams1 or not ngrams2:
            return 0.0
        
        # Calculate Jaccard similarity
        set1 = set(ngrams1)
        set2 = set(ngrams2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def link_overlap(self, links1: List[str], links2: List[str]) -> float:
        """Calculate link overlap between profiles"""
        if not links1 or not links2:
            return 0.0
        
        # Normalize URLs
        def normalize_url(url: str) -> str:
            url = url.lower().strip()
            url = re.sub(r'^https?://', '', url)
            url = re.sub(r'^www\.', '', url)
            url = url.rstrip('/')
            return url
        
        norm_links1 = set(normalize_url(link) for link in links1 if link)
        norm_links2 = set(normalize_url(link) for link in links2 if link)
        
        if not norm_links1 or not norm_links2:
            return 0.0
        
        intersection = len(norm_links1 & norm_links2)
        union = len(norm_links1 | norm_links2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    async def compute_identity_confidence(
        self,
        result1: 'FootprintResult',
        result2: 'FootprintResult',
        query_inputs: 'QueryInputs'
    ) -> float:
        """Compute overall identity confidence score between two results"""
        scores = {}
        
        # Username similarity
        if result1.username and result2.username:
            scores['username'] = self.username_similarity(result1.username, result2.username)
        else:
            scores['username'] = 0.0
        
        # Avatar similarity
        avatar_hash1 = await self.fetch_avatar_hash(result1.avatar_url)
        avatar_hash2 = await self.fetch_avatar_hash(result2.avatar_url)
        scores['avatar'] = self.avatar_similarity(avatar_hash1, avatar_hash2)
        
        # Bio similarity
        scores['bio'] = self.bio_similarity(result1.bio, result2.bio)
        
        # Stylometry (writing style)
        texts1 = [post.get('content', '') for post in result1.posts[:10]] + \
                 [comment.get('content', '') for comment in result1.comments[:10]]
        texts2 = [post.get('content', '') for post in result2.posts[:10]] + \
                 [comment.get('content', '') for comment in result2.comments[:10]]
        scores['stylometry'] = self.stylometry_similarity(texts1, texts2)
        
        # Link overlap
        scores['links'] = self.link_overlap(result1.links, result2.links)
        
        # Weighted average
        weights = {
            'username': 0.30,
            'avatar': 0.25,
            'bio': 0.20,
            'stylometry': 0.15,
            'links': 0.10
        }
        
        overall_score = sum(scores[key] * weights[key] for key in weights)
        
        # Boost if username matches query
        if query_inputs.usernames:
            for q_username in query_inputs.usernames:
                if result1.username and self.username_similarity(q_username, result1.username) > 0.8:
                    overall_score = min(1.0, overall_score + 0.1)
                if result2.username and self.username_similarity(q_username, result2.username) > 0.8:
                    overall_score = min(1.0, overall_score + 0.1)
        
        return float(max(0.0, min(1.0, overall_score)))

