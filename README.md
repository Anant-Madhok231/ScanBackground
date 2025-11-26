# FootprintScan

A comprehensive digital footprint scanning system that searches the entire public internet for a person's digital presence across multiple platforms, forums, blogs, archives, and search engines.

## Features

- **Modular Scraper Architecture**: Easily extensible plugin system for adding new platform scrapers
- **Multi-Platform Scanning**: Supports Reddit, Twitter, Instagram, TikTok, YouTube, Pinterest, Tumblr, Quora, Medium, WordPress, Disqus, Pastebin, and more
- **Identity Matching**: Advanced confidence scoring using username similarity, avatar hashing, bio embeddings, stylometry, and link overlap
- **Risk Analysis**: Comprehensive risk assessment including toxicity, hate speech, NSFW detection, political intensity, sentiment analysis, and posting volatility
- **Timeline Visualization**: Chronological timeline of all discovered activities
- **JSON Export**: Export complete scan results for further analysis
- **Modern UI**: Beautiful Next.js frontend with real-time progress tracking
- **Production Ready**: Docker support, CI/CD pipelines, and deployment configurations

## Architecture

### Backend (FastAPI + Python)

- **FastAPI**: Async REST API with automatic OpenAPI documentation
- **Modular Scrapers**: Each platform has its own scraper module implementing a common interface
- **Parallel Execution**: All scrapers run concurrently for maximum performance
- **NLP Analysis**: Sentence transformers for bio similarity, NLTK for sentiment analysis
- **Identity Matching**: Multi-factor confidence scoring system
- **Risk Pipeline**: Automated content risk assessment

### Frontend (Next.js + TypeScript)

- **Next.js 14**: React framework with static export for GitHub Pages
- **TypeScript**: Full type safety
- **Real-time Progress**: Live scanning progress updates
- **Responsive Design**: Works on all device sizes
- **Export Functionality**: Download scan results as JSON

## Project Structure

```
Background-check/
├── backend/
│   ├── scrapers/
│   │   ├── base_scraper.py          # Base scraper interface
│   │   ├── reddit.py
│   │   ├── twitter.py
│   │   ├── instagram.py
│   │   ├── tiktok.py
│   │   ├── youtube.py
│   │   ├── pinterest.py
│   │   ├── tumblr.py
│   │   ├── quora.py
│   │   ├── medium.py
│   │   ├── wordpress.py
│   │   ├── disqus.py
│   │   ├── pastebin.py
│   │   ├── generic_forum.py
│   │   ├── google_search.py
│   │   ├── bing_search.py
│   │   ├── linkedin.py
│   │   └── github.py
│   ├── models.py                     # Pydantic models
│   ├── scraper_manager.py            # Dynamic scraper loader
│   ├── identity_matcher.py           # Identity confidence scoring
│   ├── risk_analyzer.py              # Risk analysis pipeline
│   ├── timeline_builder.py           # Timeline generation
│   ├── main.py                       # FastAPI application
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── pages/
│   │   ├── index.tsx                 # Main scanning interface
│   │   └── _app.tsx
│   ├── types/
│   │   └── index.ts                  # TypeScript type definitions
│   ├── styles/
│   │   └── globals.css
│   ├── package.json
│   ├── tsconfig.json
│   └── next.config.js
├── .github/
│   └── workflows/
│       ├── frontend-deploy.yml       # GitHub Pages deployment
│       └── backend-ci.yml            # Backend CI/CD
└── README.md

```

## Setup Instructions

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data** (if not auto-downloaded):
   ```python
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
   ```

5. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (optional)
   ```

6. **Run the server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`
   API documentation at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set environment variable** (optional, defaults to localhost):
   ```bash
   # Create .env.local
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Run development server**:
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:3000`

5. **Build for production**:
   ```bash
   npm run build
   npm run export
   ```

## Docker Deployment

### Backend

1. **Build the image**:
   ```bash
   cd backend
   docker build -t footprintscan-backend .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8000:8000 --env-file .env footprintscan-backend
   ```

## GitHub Pages Deployment

### Frontend

1. **Configure GitHub Actions**:
   - The workflow is already set up in `.github/workflows/frontend-deploy.yml`
   - Push to `main` branch to trigger deployment
   - Set `NEXT_PUBLIC_API_URL` in GitHub Secrets if needed

2. **Manual deployment**:
   ```bash
   cd frontend
   npm run build
   npm run export
   # Deploy the 'out' directory to GitHub Pages
   ```

## API Endpoints

### `GET /`
Health check and API information

### `GET /health`
Health status endpoint

### `POST /scan`
Main scanning endpoint

**Request Body**:
```json
{
  "name": "John Doe",
  "usernames": ["johndoe", "jdoe"],
  "email": "john.doe@example.com"
}
```

**Response**: Complete scan results with footprints, confidence scores, risk analysis, and timeline

### `GET /docs`
Interactive API documentation (Swagger UI)

## Adding New Scrapers

To add a new platform scraper:

1. **Create a new file** in `backend/scrapers/`:
   ```python
   from scrapers.base_scraper import Scraper
   from models import FootprintResult, QueryInputs, Platform
   
   class NewPlatformScraper(Scraper):
       async def search(self, query_inputs: QueryInputs) -> List[FootprintResult]:
           # Your scraping logic here
           results = []
           # ... implementation
           return results
   ```

2. **Add to scraper list** in `scraper_manager.py`:
   ```python
   scraper_modules = [
       # ... existing scrapers
       'new_platform',
   ]
   ```

3. **The scraper will be automatically loaded** on next server start

## Identity Matching

The system uses multiple factors to calculate confidence scores:

- **Username Similarity** (30%): String matching and similarity algorithms
- **Avatar Similarity** (25%): Perceptual hashing of profile images
- **Bio Similarity** (20%): Semantic embeddings using sentence transformers
- **Stylometry** (15%): Writing style analysis using n-gram patterns
- **Link Overlap** (10%): Cross-platform link sharing patterns

## Risk Analysis

Each post/comment is analyzed for:

- **Toxicity** (40%): Insulting language, aggressive tone
- **Hate Speech** (20%): Discriminatory content
- **NSFW Content** (15%): Adult/explicit material
- **Political Intensity** (15%): Political content frequency
- **Volatility** (10%): Posting pattern irregularity

**Overall Risk Score** = `(0.40*toxicity + 0.20*hate + 0.15*nsfw + 0.15*politics + 0.10*volatility) * 100`

## Environment Variables

### Backend (.env)

```env
# API Keys (optional)
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
TWITTER_BEARER_TOKEN=
INSTAGRAM_ACCESS_TOKEN=
YOUTUBE_API_KEY=
GOOGLE_SEARCH_API_KEY=
GOOGLE_SEARCH_ENGINE_ID=
BING_SEARCH_API_KEY=

# Server Configuration
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,https://yourusername.github.io

# NLP Models
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
```

## Legal and Ethical Considerations

⚠️ **Important**: This tool is designed for:
- Personal digital footprint analysis
- Background checks with consent
- Security research
- OSINT (Open Source Intelligence) gathering

**Do NOT use for**:
- Unauthorized surveillance
- Harassment or stalking
- Violating platform terms of service
- Accessing private or protected information

All scrapers use only public, legal endpoints. No authentication bypassing or private API access is performed.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your scraper or improvement
4. Submit a pull request

## License

This project is provided as-is for educational and research purposes.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Roadmap

- [ ] Additional platform scrapers
- [ ] Machine learning-based identity matching
- [ ] Real-time scanning with WebSockets
- [ ] Advanced visualization dashboard
- [ ] Database persistence for scan history
- [ ] User authentication and scan management
- [ ] API rate limiting and caching
- [ ] Enhanced risk analysis models

---

**FootprintScan** - Comprehensive Digital Footprint Analysis

