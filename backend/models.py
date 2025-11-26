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

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class Platform(str, Enum):
    REDDIT = "reddit"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    PINTEREST = "pinterest"
    TUMBLR = "tumblr"
    QUORA = "quora"
    MEDIUM = "medium"
    WORDPRESS = "wordpress"
    DISQUS = "disqus"
    PASTEBIN = "pastebin"
    FORUM = "forums"
    BLOG = "blogs"
    ARCHIVE = "archives"
    SEARCH_RESULT = "search_results"
    OTHER = "other"


class QueryInputs(BaseModel):
    name: Optional[str] = None
    usernames: List[str] = Field(default_factory=list)
    email: Optional[str] = None


class FootprintResult(BaseModel):
    platform: Platform
    username: Optional[str] = None
    profile_url: str
    profile_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    posts: List[Dict[str, Any]] = Field(default_factory=list)
    comments: List[Dict[str, Any]] = Field(default_factory=list)
    links: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RiskMetrics(BaseModel):
    toxicity: float = Field(ge=0.0, le=1.0)
    hate_speech: float = Field(ge=0.0, le=1.0)
    nsfw: float = Field(ge=0.0, le=1.0)
    political_intensity: float = Field(ge=0.0, le=1.0)
    sentiment: float = Field(ge=-1.0, le=1.0)  # -1 negative, 1 positive
    volatility: float = Field(ge=0.0, le=1.0)
    overall_risk: float = Field(ge=0.0, le=100.0)


class RiskAnalysis(BaseModel):
    post_id: str
    platform: Platform
    content: str
    timestamp: Optional[datetime] = None
    url: Optional[str] = None
    metrics: RiskMetrics
    flagged: bool = False
    flags: List[str] = Field(default_factory=list)


class TimelineEntry(BaseModel):
    timestamp: datetime
    platform: Platform
    type: str  # "post", "comment", "account_created"
    content: str
    url: Optional[str] = None
    risk_score: float = Field(ge=0.0, le=100.0)


class ConfidenceScore(BaseModel):
    platform: Platform
    username: Optional[str] = None
    score: float = Field(ge=0.0, le=1.0)
    factors: Dict[str, float] = Field(default_factory=dict)


class ScanResponse(BaseModel):
    accounts_found: int
    footprints: Dict[str, List[FootprintResult]] = Field(default_factory=dict)
    confidence_scores: List[ConfidenceScore] = Field(default_factory=list)
    risk_analysis: List[RiskAnalysis] = Field(default_factory=list)
    timeline: List[TimelineEntry] = Field(default_factory=list)
    exportable_report: Dict[str, Any] = Field(default_factory=dict)
    scan_id: str
    scan_timestamp: datetime

