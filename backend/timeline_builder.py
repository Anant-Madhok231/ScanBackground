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

from typing import List, Dict, Any
from datetime import datetime
from models import TimelineEntry, Platform, FootprintResult


class TimelineBuilder:
    def build_timeline(self, footprints: Dict[str, List[FootprintResult]], risk_analysis: List[Dict[str, Any]]) -> List[TimelineEntry]:
        """Build chronological timeline from all footprints and risk analysis"""
        timeline_entries = []
        
        # Create risk lookup by content/URL
        risk_lookup = {}
        for risk in risk_analysis:
            key = risk.get('url') or risk.get('post_id', '')
            risk_lookup[key] = risk
        
        # Extract all timeline entries from footprints
        for platform, results in footprints.items():
            for result in results:
                # Add account creation (estimated from first post)
                if result.posts:
                    first_post = result.posts[0]
                    if 'timestamp' in first_post:
                        try:
                            ts = self._parse_timestamp(first_post['timestamp'])
                            try:
                                platform_enum = Platform(platform)
                            except ValueError:
                                platform_enum = Platform.OTHER
                            timeline_entries.append(TimelineEntry(
                                timestamp=ts,
                                platform=platform_enum,
                                type="account_created",
                                content=f"Account created on {platform}",
                                url=result.profile_url,
                                risk_score=0.0
                            ))
                        except Exception:
                            pass
                
                # Add posts
                for post in result.posts:
                    if 'timestamp' in post:
                        try:
                            ts = self._parse_timestamp(post['timestamp'])
                            content = post.get('content', post.get('title', ''))
                            url = post.get('url', result.profile_url)
                            
                            # Get risk score
                            risk_score = 0.0
                            if url in risk_lookup:
                                risk_score = risk_lookup[url].get('metrics', {}).get('overall_risk', 0.0)
                            
                            try:
                                platform_enum = Platform(platform)
                            except ValueError:
                                platform_enum = Platform.OTHER
                            timeline_entries.append(TimelineEntry(
                                timestamp=ts,
                                platform=platform_enum,
                                type="post",
                                content=content[:200],  # Truncate for display
                                url=url,
                                risk_score=risk_score
                            ))
                        except Exception:
                            pass
                
                # Add comments
                for comment in result.comments:
                    if 'timestamp' in comment:
                        try:
                            ts = self._parse_timestamp(comment['timestamp'])
                            content = comment.get('content', '')
                            url = comment.get('url', result.profile_url)
                            
                            # Get risk score
                            risk_score = 0.0
                            if url in risk_lookup:
                                risk_score = risk_lookup[url].get('metrics', {}).get('overall_risk', 0.0)
                            
                            try:
                                platform_enum = Platform(platform)
                            except ValueError:
                                platform_enum = Platform.OTHER
                            timeline_entries.append(TimelineEntry(
                                timestamp=ts,
                                platform=platform_enum,
                                type="comment",
                                content=content[:200],  # Truncate for display
                                url=url,
                                risk_score=risk_score
                            ))
                        except Exception:
                            pass
        
        # Sort by timestamp
        timeline_entries.sort(key=lambda x: x.timestamp)
        
        return timeline_entries
    
    def _parse_timestamp(self, timestamp: Any) -> datetime:
        """Parse timestamp from various formats"""
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, str):
            # Try ISO format
            try:
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                pass
            
            # Try common formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp, fmt)
                except ValueError:
                    continue
        
        # Default to now if parsing fails
        return datetime.now()

