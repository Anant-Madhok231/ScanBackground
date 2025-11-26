# API Setup Guide for FootprintScan

This document lists all the APIs used by FootprintScan scrapers and how to obtain API keys.

## APIs Currently Implemented

### ✅ Reddit API (PRAW)
- **Status**: Fully implemented
- **API**: Reddit API via PRAW library
- **Get Keys**: https://www.reddit.com/prefs/apps
- **Required**: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`
- **Features**: User profiles, posts, comments

### ✅ Twitter/X API v2
- **Status**: Fully implemented
- **API**: Twitter API v2
- **Get Keys**: https://developer.twitter.com/en/portal/dashboard
- **Required**: `TWITTER_BEARER_TOKEN`
- **Features**: User profiles, tweets, user metadata

### ✅ YouTube Data API v3
- **Status**: Fully implemented
- **API**: YouTube Data API v3
- **Get Keys**: https://console.cloud.google.com/apis/credentials
- **Required**: `YOUTUBE_API_KEY`
- **Features**: Channel info, videos, playlists

### ✅ Instagram Basic Display API
- **Status**: Implemented (requires OAuth)
- **API**: Instagram Graph API / Basic Display API
- **Get Keys**: https://developers.facebook.com/docs/instagram-basic-display-api
- **Required**: `INSTAGRAM_ACCESS_TOKEN`
- **Features**: User profile, media posts
- **Note**: Requires OAuth flow for access tokens

### ✅ GitHub API
- **Status**: Fully implemented
- **API**: GitHub REST API v3
- **Get Keys**: https://github.com/settings/tokens (optional, increases rate limit)
- **Required**: `GITHUB_TOKEN` (optional)
- **Features**: User profiles, repositories, activity events
- **Note**: Works without token but has rate limits

### ✅ Google Custom Search API
- **Status**: Fully implemented
- **API**: Google Custom Search JSON API
- **Get Keys**: https://developers.google.com/custom-search/v1/overview
- **Required**: `GOOGLE_SEARCH_API_KEY`, `GOOGLE_SEARCH_ENGINE_ID`
- **Features**: Web search results for digital footprints

### ✅ Bing Web Search API
- **Status**: Fully implemented
- **API**: Bing Web Search API v7
- **Get Keys**: https://www.microsoft.com/en-us/bing/apis/bing-web-search-api
- **Required**: `BING_SEARCH_API_KEY`
- **Features**: Web search results for digital footprints

### 🔄 Other Platforms (HTML Parsing)
The following platforms use HTML parsing (no API required):
- TikTok
- Pinterest
- Tumblr
- Quora (with HTML parsing)
- Medium (with HTML parsing)
- WordPress
- Disqus
- Pastebin
- LinkedIn
- Generic Forums

## Quick Setup

1. **Copy environment file**:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Add your API keys to `.env`**:
   ```env
   REDDIT_CLIENT_ID=your_reddit_client_id
   REDDIT_CLIENT_SECRET=your_reddit_secret
   TWITTER_BEARER_TOKEN=your_twitter_token
   YOUTUBE_API_KEY=your_youtube_key
   GOOGLE_SEARCH_API_KEY=your_google_key
   GOOGLE_SEARCH_ENGINE_ID=your_engine_id
   BING_SEARCH_API_KEY=your_bing_key
   GITHUB_TOKEN=your_github_token  # Optional
   INSTAGRAM_ACCESS_TOKEN=your_instagram_token  # Requires OAuth
   ```

3. **Restart the backend**:
   ```bash
   uvicorn main:app --reload
   ```

## API Rate Limits

- **Reddit**: 60 requests/minute (with OAuth)
- **Twitter**: Varies by plan (Free tier: 1,500 requests/month)
- **YouTube**: 10,000 units/day (default quota)
- **GitHub**: 60 requests/hour (unauthenticated), 5,000/hour (authenticated)
- **Google Search**: 100 requests/day (free tier)
- **Bing Search**: Varies by plan

## Notes

- **Without API keys**: Scrapers will still attempt to find profiles using HTML parsing, but results will be limited
- **With API keys**: Full access to user data, posts, comments, and metadata
- **Instagram**: Requires OAuth flow - most complex to set up
- **Twitter**: Free tier has limited requests, consider upgrading for production use

## Testing APIs

You can test if your API keys work by checking the `/` endpoint:
```bash
curl http://localhost:8000/
```

This will show how many scrapers are loaded. Scrapers with missing API keys will still load but return limited results.

