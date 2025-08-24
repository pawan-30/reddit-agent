from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import os
import json
import uuid
import asyncio
import requests
from bs4 import BeautifulSoup
import re
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv()

router = APIRouter()

app = FastAPI(title="Reddit Tracking Agent")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
# MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://user:<reddit123>@reddit.kbmr4rf.mongodb.net/?retryWrites=true&w=majority&appName=reddit")
client = AsyncIOMotorClient(
    "mongodb+srv://user:123@reddit.kbmr4rf.mongodb.net/?retryWrites=true&w=majority&appName=reddit"
)
db = client.get_database("reddit")  # Replace with your actual DB name

# Pydantic models
class SearchRequest(BaseModel):
    query: str
    company_description: str = ""
    max_posts: int = Field(default=20, ge=1, le=100)

class RedditPost(BaseModel):
    id: str
    title: str
    content: str
    subreddit: str
    author: str
    upvotes: int
    comments_count: int
    url: str
    created_at: str
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PostAnalysis(BaseModel):
    post_id: str
    relevance_score: float
    takeaways: List[str]
    suggested_response: str
    targeting_insights: str
    analysis_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TrendSynthesis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query: str
    posts_analyzed: int
    key_trends: List[str]
    community_insights: Dict[str, Any]
    suggested_strategies: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Target subreddits
TARGET_SUBREDDITS = [
    "longevity", "Futurology", "science", "Biohackers", 
    "artificial", "singularity", "health", "mitochondria", 
    "aging", "QuantifiedSelf"
]

class RedditScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def scrape_with_pushshift(self, subreddit: str, query: str, limit: int = 10) -> List[Dict]:
        """Try using Pushshift API as an alternative"""
        try:
            # Pushshift API endpoint
            url = f"https://api.pushshift.io/reddit/search/submission/"
            params = {
                'subreddit': subreddit,
                'q': query,
                'size': limit,
                'sort': 'score',
                'sort_type': 'desc'
            }
            
            import time
            time.sleep(0.5)
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                posts = []
                
                for item in data.get('data', []):
                    if not item.get('title'):
                        continue
                        
                    post = {
                        'id': item.get('id', ''),
                        'title': item.get('title', ''),
                        'content': item.get('selftext', ''),
                        'subreddit': subreddit,
                        'author': item.get('author', '[deleted]'),
                        'upvotes': item.get('score', 0),
                        'comments_count': item.get('num_comments', 0),
                        'url': f"https://www.reddit.com/r/{subreddit}/comments/{item.get('id', '')}",
                        'created_at': str(datetime.fromtimestamp(item.get('created_utc', 0), tz=timezone.utc)),
                        'score': item.get('score', 0)
                    }
                    posts.append(post)
                    
                return posts
        except Exception as e:
            print(f"Error with Pushshift for r/{subreddit}: {e}")
            return []

    def scrape_subreddit_search(self, subreddit: str, query: str, limit: int = 10) -> List[Dict]:
        """Search posts within a specific subreddit using multiple methods"""
        try:
            # Try multiple Reddit endpoints
            search_urls = [
                f"https://www.reddit.com/r/{subreddit}/search.json?q={query}&restrict_sr=1&sort=relevance&limit={limit}",
                f"https://www.reddit.com/search.json?q={query}+subreddit:{subreddit}&sort=relevance&limit={limit}",
            ]
            
            for search_url in search_urls:
                try:
                    import time
                    time.sleep(1)  # Rate limiting
                    
                    response = self.session.get(search_url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        posts = []
                        
                        for item in data.get('data', {}).get('children', []):
                            post_data = item.get('data', {})
                            
                            # Skip if deleted or removed
                            if post_data.get('removed_by_category') or not post_data.get('title'):
                                continue
                                
                            post = {
                                'id': post_data.get('id', ''),
                                'title': post_data.get('title', ''),
                                'content': post_data.get('selftext', ''),
                                'subreddit': subreddit,
                                'author': post_data.get('author', '[deleted]'),
                                'upvotes': post_data.get('ups', 0),
                                'comments_count': post_data.get('num_comments', 0),
                                'url': f"https://www.reddit.com{post_data.get('permalink', '')}",
                                'created_at': str(datetime.fromtimestamp(post_data.get('created_utc', 0), tz=timezone.utc)),
                                'score': post_data.get('score', 0)
                            }
                            posts.append(post)
                            
                        if posts:  # If we got posts, return them
                            return posts
                        
                except requests.exceptions.RequestException as e:
                    print(f"Failed {search_url}: {e}")
                    continue
                    
            # If Reddit APIs fail, try Pushshift
            pushshift_posts = self.scrape_with_pushshift(subreddit, query, limit)
            if pushshift_posts:
                return pushshift_posts
                
            return []
        except Exception as e:
            print(f"Error searching r/{subreddit} for '{query}': {e}")
            return []

    def scrape_subreddit_hot(self, subreddit: str, limit: int = 10) -> List[Dict]:
        """Scrape hot posts from a subreddit using multiple methods"""
        try:
            # Try multiple approaches
            urls_to_try = [
                f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}",
                f"https://www.reddit.com/r/{subreddit}.json?limit={limit}",
                f"https://www.reddit.com/r/{subreddit}/top.json?t=week&limit={limit}",
            ]
            
            for url in urls_to_try:
                try:
                    import time
                    time.sleep(0.5)  # Rate limiting
                    
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        posts = []
                        
                        for item in data.get('data', {}).get('children', []):
                            post_data = item.get('data', {})
                            
                            # Skip if deleted or removed
                            if post_data.get('removed_by_category') or not post_data.get('title'):
                                continue
                                
                            post = {
                                'id': post_data.get('id', ''),
                                'title': post_data.get('title', ''),
                                'content': post_data.get('selftext', ''),
                                'subreddit': subreddit,
                                'author': post_data.get('author', '[deleted]'),
                                'upvotes': post_data.get('ups', 0),
                                'comments_count': post_data.get('num_comments', 0),
                                'url': f"https://www.reddit.com{post_data.get('permalink', '')}",
                                'created_at': str(datetime.fromtimestamp(post_data.get('created_utc', 0), tz=timezone.utc)),
                                'score': post_data.get('score', 0)
                            }
                            posts.append(post)
                            
                        return posts
                        
                except requests.exceptions.RequestException as e:
                    print(f"Failed {url}: {e}")
                    continue
                    
            return []
        except Exception as e:
            print(f"Error scraping r/{subreddit}: {e}")
            return []

    def search_reddit(self, query: str, subreddits: List[str], max_posts: int = 20) -> List[Dict]:
        """Search Reddit posts across multiple subreddits"""
        all_posts = []
        posts_per_subreddit = max(2, max_posts // len(subreddits))
        
        # First try targeted search within each subreddit
        for subreddit in subreddits:
            # Try search first
            search_posts = self.scrape_subreddit_search(subreddit, query, posts_per_subreddit // 2)
            all_posts.extend(search_posts)
            
            # If search didn't return enough, get hot posts
            if len(search_posts) < posts_per_subreddit // 2:
                hot_posts = self.scrape_subreddit_hot(subreddit, posts_per_subreddit - len(search_posts))
                # Filter hot posts by query relevance
                relevant_hot_posts = [
                    post for post in hot_posts 
                    if any(keyword.lower() in post['title'].lower() or keyword.lower() in post['content'].lower() 
                           for keyword in query.split())
                ]
                all_posts.extend(relevant_hot_posts)
            
        # Remove duplicates based on post ID
        seen_ids = set()
        unique_posts = []
        for post in all_posts:
            if post['id'] not in seen_ids:
                seen_ids.add(post['id'])
                unique_posts.append(post)
        
        # Sort by score and limit
        unique_posts.sort(key=lambda x: x.get('score', 0), reverse=True)
        return unique_posts[:max_posts]

# Mock analysis function for testing
def mock_analyze_post(post):
    """Mock analysis function that returns dummy data"""
    # Simple relevance scoring based on keywords
    health_keywords = ['health', 'wellness', 'AI', 'personalized', 'biohacking', 'longevity', 'aging', 'fitness']
    title_lower = post['title'].lower()
    content_lower = post['content'].lower()
    
    relevance_score = 0
    for keyword in health_keywords:
        if keyword in title_lower:
            relevance_score += 15
        if keyword in content_lower:
            relevance_score += 10
    
    relevance_score = min(relevance_score, 100)
    
    return {
        "relevance_score": relevance_score,
        "takeaways": [
            f"Post discusses {post['subreddit']} community interests",
            f"Received {post['upvotes']} upvotes indicating community engagement",
            "Potential opportunity for Eon Health engagement"
        ],
        "suggested_response": f"Great insights! At Eon Health, we're working on similar personalized health solutions.",
        "targeting_insights": f"The r/{post['subreddit']} community shows interest in health optimization topics."
    }

def create_demonstration_posts(query: str) -> List[RedditPost]:
    """Create demonstration posts that show how the agent would work with real data"""
    demo_data = [
        {
            'id': f'demo_{hash(query) % 1000}_1',
            'title': f'New breakthrough in personalized {query} research - AI predicts optimal interventions',
            'content': f'Researchers have developed an AI system that can predict the most effective {query} interventions for individuals based on their genetic markers, lifestyle data, and biomarkers. Early trials show 40% better outcomes compared to standard approaches. The system integrates data from wearables and lab tests to provide personalized recommendations.',
            'subreddit': 'longevity',
            'author': f'{query}_researcher_2024',
            'upvotes': 342,
            'comments_count': 87,
            'url': f'https://www.reddit.com/r/longevity/comments/demo_{query}_research/',
            'created_at': str(datetime.now(timezone.utc) - timedelta(hours=6)),
            'score': 342
        },
        {
            'id': f'demo_{hash(query) % 1000}_2',
            'title': f'How wearable tech is revolutionizing {query} tracking - my 6-month experiment',
            'content': f'I spent 6 months tracking every aspect of my health using various wearables and apps. The data revealed surprising insights about my {query} patterns and helped me optimize my lifestyle. Here are the key findings and recommendations for anyone interested in self-quantification.',
            'subreddit': 'QuantifiedSelf',
            'author': 'biohacker_qself',
            'upvotes': 156,
            'comments_count': 43,
            'url': f'https://www.reddit.com/r/QuantifiedSelf/comments/demo_wearable_{query}/',
            'created_at': str(datetime.now(timezone.utc) - timedelta(hours=12)),
            'score': 156
        },
        {
            'id': f'demo_{hash(query) % 1000}_3',
            'title': f'The future of {query}: AI-driven preventive medicine in 2024',
            'content': f'Major healthcare companies are investing billions in AI systems that can predict health outcomes decades in advance. These systems analyze genomic data, environmental factors, and lifestyle choices to provide personalized {query} recommendations. What does this mean for the future of healthcare?',
            'subreddit': 'Futurology',
            'author': 'future_health_expert',
            'upvotes': 289,
            'comments_count': 92,
            'url': f'https://www.reddit.com/r/Futurology/comments/demo_ai_{query}_future/',
            'created_at': str(datetime.now(timezone.utc) - timedelta(hours=18)),
            'score': 289
        },
        {
            'id': f'demo_{hash(query) % 1000}_4',
            'title': f'Scientific study: Personalized nutrition based on microbiome analysis improves {query}',
            'content': f'A new peer-reviewed study published in Nature shows that personalized nutrition recommendations based on individual microbiome analysis can significantly improve {query} outcomes. The study followed 1,200 participants over 2 years and found personalized interventions were 3x more effective than generic advice.',
            'subreddit': 'science',
            'author': 'science_communicator',
            'upvotes': 421,
            'comments_count': 134,
            'url': f'https://www.reddit.com/r/science/comments/demo_microbiome_{query}/',
            'created_at': str(datetime.now(timezone.utc) - timedelta(hours=24)),
            'score': 421
        }
    ]
    
    demo_posts = []
    for post_data in demo_data:
        demo_posts.append(RedditPost(**post_data))
    
    return demo_posts

# API Routes
@app.post("/api/search-reddit")
async def search_reddit_posts(request: SearchRequest):
    """Search and analyze Reddit posts"""
    try:
        scraper = RedditScraper()
        
        # Search Reddit posts
        posts = scraper.search_reddit(request.query, TARGET_SUBREDDITS, request.max_posts)
        
        if not posts:
            return {
                "message": f"No posts found for '{request.query}'. Reddit may be blocking requests or no relevant posts exist in the target communities.",
                "posts": [], 
                "query": request.query,
                "suggestion": "Try different keywords or check if the subreddits contain relevant discussions."
            }
        
        # Store posts in database
        stored_posts = []
        for post_data in posts:
            reddit_post = RedditPost(**post_data)
            
            # Check if post already exists
            existing = await db.reddit_posts.find_one({"id": reddit_post.id})
            if not existing:
                # Convert to dict and ensure proper serialization
                post_dict = reddit_post.dict()
                # Convert datetime to ISO string for MongoDB storage
                if isinstance(post_dict.get('scraped_at'), datetime):
                    post_dict['scraped_at'] = post_dict['scraped_at'].isoformat()
                await db.reddit_posts.insert_one(post_dict)
            stored_posts.append(reddit_post)
        
        return {
            "message": f"Found {len(stored_posts)} posts from Reddit search for '{request.query}'",
            "posts": [post.dict() for post in stored_posts],
            "query": request.query
        }
        
    except Exception as e:
        print(f"Error in search_reddit_posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-posts")
async def analyze_posts(post_ids: List[str]):
    """Analyze posts for relevance and extract insights"""
    try:
        analyses = []
        
        for post_id in post_ids:
            # Get post from database
            post = await db.reddit_posts.find_one({"id": post_id})
            if not post:
                continue
                
            # Check if analysis already exists
            existing_analysis = await db.post_analyses.find_one({"post_id": post_id}, {"_id": 0})
            if existing_analysis:
                analyses.append(existing_analysis)
                continue
            
            # Mock analysis for testing
            analysis_data = mock_analyze_post(post)
            
            # Create analysis object
            analysis = PostAnalysis(
                post_id=post_id,
                relevance_score=float(analysis_data.get('relevance_score', 0)),
                takeaways=analysis_data.get('takeaways', []),
                suggested_response=analysis_data.get('suggested_response', ''),
                targeting_insights=analysis_data.get('targeting_insights', '')
            )
            
            # Store analysis
            await db.post_analyses.insert_one(analysis.dict())
            analyses.append(analysis.dict())
                
        return {"analyses": analyses}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/synthesize-trends")
async def synthesize_trends(query: str, min_relevance: float = 50.0):
    """Synthesize trends from analyzed posts"""
    try:
        # Get high-relevance analyses
        analyses = await db.post_analyses.find(
            {"relevance_score": {"$gte": min_relevance}}
        ).to_list(length=None)
        
        if len(analyses) < 2:
            return {"message": "Not enough relevant posts for trend analysis"}
        
        # Mock trend synthesis
        trend_synthesis = TrendSynthesis(
            query=query,
            posts_analyzed=len(analyses),
            key_trends=[
                "Increasing interest in personalized health solutions",
                "Growing adoption of AI in healthcare",
                "Community focus on preventive medicine",
                "Rising popularity of biohacking techniques",
                "Integration of wearable technology with health monitoring"
            ],
            community_insights={
                "r/longevity": "Highly engaged community focused on extending healthspan",
                "r/Biohackers": "Tech-savvy users interested in self-optimization",
                "r/science": "Evidence-based discussions about health research"
            },
            suggested_strategies=[
                "Engage with longevity community through educational content",
                "Share research-backed insights in science communities",
                "Participate in biohacking discussions with practical tips"
            ]
        )
        
        # Store synthesis
        await db.trend_syntheses.insert_one(trend_synthesis.dict())
        
        return trend_synthesis.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/posts")
async def get_posts(limit: int = 50, min_relevance: Optional[float] = None):
    """Get stored posts with optional relevance filtering"""
    try:
        # Get posts
        posts = await db.reddit_posts.find({}, {"_id": 0}).sort("scraped_at", -1).limit(limit).to_list(length=None)
        
        # Get analyses
        post_ids = [post['id'] for post in posts]
        analyses = await db.post_analyses.find(
            {"post_id": {"$in": post_ids}}, {"_id": 0}
        ).to_list(length=None)
        
        # Create analyses lookup
        analyses_lookup = {analysis['post_id']: analysis for analysis in analyses}
        
        # Combine posts with analyses
        enhanced_posts = []
        for post in posts:
            analysis = analyses_lookup.get(post['id'])
            if min_relevance and analysis:
                if analysis['relevance_score'] < min_relevance:
                    continue
            
            post['analysis'] = analysis
            enhanced_posts.append(post)
        
        return {"posts": enhanced_posts}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trends")
async def get_trends(limit: int = 10):
    """Get trend syntheses"""
    try:
        trends = await db.trend_syntheses.find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(length=None)
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)