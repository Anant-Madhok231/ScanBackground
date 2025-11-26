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
import uuid
from datetime import datetime
from typing import Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from models import QueryInputs, ScanResponse, FootprintResult, Platform, RiskAnalysis, RiskMetrics, ConfidenceScore, TimelineEntry
from scraper_manager import ScraperManager
from identity_matcher import IdentityMatcher
from risk_analyzer import RiskAnalyzer
from timeline_builder import TimelineBuilder

load_dotenv()

app = FastAPI(
    title="FootprintScan API",
    description="Digital footprint scanning API",
    version="1.0.0"
)

# CORS configuration
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
scraper_manager = ScraperManager()
identity_matcher = IdentityMatcher()
risk_analyzer = RiskAnalyzer()
timeline_builder = TimelineBuilder()


@app.get("/")
async def root():
    return {
        "message": "FootprintScan API",
        "version": "1.0.0",
        "scrapers_loaded": scraper_manager.get_scraper_count()
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/scan", response_model=ScanResponse)
async def scan(query_inputs: QueryInputs):
    """Main scanning endpoint"""
    try:
        # Validate inputs
        if not query_inputs.name and not query_inputs.usernames and not query_inputs.email:
            raise HTTPException(status_code=400, detail="At least one of name, usernames, or email must be provided")
        
        # Run all scrapers in parallel
        all_results = await scraper_manager.run_all_scrapers(query_inputs)
        
        # Group results by platform and filter by confidence
        footprints: Dict[str, List[FootprintResult]] = {}
        for result in all_results:
            # Include results with confidence > 0 (meaning name matched)
            if result.confidence_score <= 0.0:
                continue
                
            platform_key = result.platform.value
            if platform_key not in footprints:
                footprints[platform_key] = []
            footprints[platform_key].append(result)
        
        # Sort results by confidence within each platform
        for platform_key in footprints:
            footprints[platform_key].sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Calculate confidence scores using identity matcher
        confidence_scores: List[ConfidenceScore] = []
        for platform_key, results in footprints.items():
            for result in results:
                # Calculate confidence based on name and username match
                confidence = result.confidence_score  # Start with scraper's confidence
                
                # STRICT name matching - verify ALL words are present
                if query_inputs.name and result.profile_name:
                    name_lower = query_inputs.name.lower().strip()
                    name_parts = [p.strip() for p in name_lower.split() if p.strip()]
                    profile_lower = result.profile_name.lower()
                    bio_lower = (result.bio or '').lower()
                    combined_text = f"{profile_lower} {bio_lower}"
                    
                    # Check if ALL name parts are present (word-for-word)
                    if len(name_parts) > 0:
                        all_parts_match = all(part in combined_text for part in name_parts)
                        
                        if all_parts_match:
                            # Exact full name match
                            if name_lower in profile_lower or name_lower in bio_lower:
                                confidence = min(1.0, confidence + 0.2)
                            # All words present
                            else:
                                confidence = min(1.0, confidence + 0.1)
                        else:
                            # Not all words match - set confidence to 0
                            confidence = 0.0
                
                # Username match
                if result.username and query_inputs.usernames:
                    for q_username in query_inputs.usernames:
                        from identity_matcher import IdentityMatcher
                        matcher = IdentityMatcher()
                        similarity = matcher.username_similarity(q_username, result.username)
                        confidence = max(confidence, similarity)
                
                # Email match
                if query_inputs.email and result.bio:
                    if query_inputs.email.lower() in result.bio.lower():
                        confidence = min(1.0, confidence + 0.15)
                
                # Update result confidence
                result.confidence_score = confidence
                
                confidence_scores.append(ConfidenceScore(
                    platform=result.platform,
                    username=result.username,
                    score=confidence,
                    factors={
                        'name_match': 0.3 if query_inputs.name and result.profile_name else 0,
                        'username_match': 0.2 if result.username else 0,
                        'email_match': 0.1 if query_inputs.email else 0,
                        'base_confidence': result.confidence_score
                    }
                ))
        
        # Perform risk analysis on all posts and comments
        risk_analyses: List[RiskAnalysis] = []
        all_posts = []
        
        for result in all_results:
            # Analyze posts
            for post in result.posts:
                content = post.get('content', '') or post.get('title', '')
                if content:
                    risk_metrics_dict = risk_analyzer.analyze_risk(content, result.posts)
                    should_flag, flags = risk_analyzer.should_flag(risk_metrics_dict)
                    
                    risk_analyses.append(RiskAnalysis(
                        post_id=post.get('url', str(uuid.uuid4())),
                        platform=result.platform,
                        content=content[:500],  # Truncate for storage
                        timestamp=datetime.fromtimestamp(post.get('timestamp', datetime.now().timestamp())) if isinstance(post.get('timestamp'), (int, float)) else None,
                        url=post.get('url'),
                        metrics=RiskMetrics(**risk_metrics_dict),
                        flagged=should_flag,
                        flags=flags
                    ))
            
            # Analyze comments
            for comment in result.comments:
                content = comment.get('content', '')
                if content:
                    risk_metrics_dict = risk_analyzer.analyze_risk(content, result.comments)
                    should_flag, flags = risk_analyzer.should_flag(risk_metrics_dict)
                    
                    risk_analyses.append(RiskAnalysis(
                        post_id=comment.get('url', str(uuid.uuid4())),
                        platform=result.platform,
                        content=content[:500],
                        timestamp=datetime.fromtimestamp(comment.get('timestamp', datetime.now().timestamp())) if isinstance(comment.get('timestamp'), (int, float)) else None,
                        url=comment.get('url'),
                        metrics=RiskMetrics(**risk_metrics_dict),
                        flagged=should_flag,
                        flags=flags
                    ))
        
        # Build timeline
        timeline = timeline_builder.build_timeline(footprints, [ra.model_dump() for ra in risk_analyses])
        
        # Create exportable report
        exportable_report = {
            'scan_id': str(uuid.uuid4()),
            'scan_timestamp': datetime.now().isoformat(),
            'query': query_inputs.model_dump(),
            'summary': {
                'total_accounts': len(all_results),
                'total_posts': sum(len(r.posts) for r in all_results),
                'total_comments': sum(len(r.comments) for r in all_results),
                'total_flagged': sum(1 for ra in risk_analyses if ra.flagged),
                'platforms_found': list(footprints.keys())
            },
            'footprints': {k: [r.model_dump() for r in v] for k, v in footprints.items()},
            'confidence_scores': [cs.model_dump() for cs in confidence_scores],
            'risk_analysis': [ra.model_dump() for ra in risk_analyses],
            'timeline': [te.model_dump() for te in timeline]
        }
        
        # Create response
        scan_id = str(uuid.uuid4())
        response = ScanResponse(
            accounts_found=len(all_results),
            footprints=footprints,
            confidence_scores=confidence_scores,
            risk_analysis=risk_analyses,
            timeline=timeline,
            exportable_report=exportable_report,
            scan_id=scan_id,
            scan_timestamp=datetime.now()
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/export/{scan_id}")
async def export_scan(scan_id: str):
    """Export scan results as JSON"""
    # In a real implementation, this would fetch from a database
    # For now, return a placeholder
    return {"message": "Export functionality - scan results should be exported from the /scan endpoint"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

