from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import os
import json
import uuid
import asyncio
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Load environment variables
load_dotenv()

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
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017/app_db")
client = AsyncIOMotorClient(MONGO_URL)
db = client.get_database()

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

# Initialize Claude chat
async def get_claude_chat():
    api_key = os.environ.get("EMERGENT_LLM_KEY")
    chat = LlmChat(
        api_key=api_key,
        session_id=str(uuid.uuid4()),
        system_message="""You are an expert analyst for Eon Health, a company that positions itself as "Your Operating System for Healthspan." 
        
        Eon Health uses AI, data science, and user-centric design to provide personalized health insights, integrating with wearable technology to deliver tailored recommendations for nutrition, exercise, sleep, and lifestyle adjustments.
        
        Key focus areas:
        - Personalized health optimization
        - AI-driven health insights
        - Wearable technology integration
        - Preventive healthcare
        - Chronic disease prevention
        - Healthspan extension (not just lifespan)
        - Scientific-backed recommendations
        
        Your role is to analyze Reddit posts and determine their relevance to Eon Health's business, extract actionable insights, and suggest engagement strategies."""
    ).with_model("anthropic", "claude-3-7-sonnet-20250219")
    return chat

class RedditScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_subreddit_hot(self, subreddit: str, limit: int = 10) -> List[Dict]:
        """Scrape hot posts from a subreddit"""
        try:
            url = f"https://www.reddit.com/r/{subreddit}/hot/.json?limit={limit}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
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
                    'url': f"https://reddit.com{post_data.get('permalink', '')}",
                    'created_at': str(datetime.fromtimestamp(post_data.get('created_utc', 0), tz=timezone.utc)),
                    'score': post_data.get('score', 0)
                }
                posts.append(post)
                
            return posts
        except Exception as e:
            print(f"Error scraping r/{subreddit}: {e}")
            return []

    def search_reddit(self, query: str, subreddits: List[str], max_posts: int = 20) -> List[Dict]:
        """Search Reddit posts across multiple subreddits"""
        all_posts = []
        posts_per_subreddit = max(1, max_posts // len(subreddits))
        
        for subreddit in subreddits:
            posts = self.scrape_subreddit_hot(subreddit, posts_per_subreddit)
            all_posts.extend(posts)
            
        # Sort by score and limit
        all_posts.sort(key=lambda x: x.get('score', 0), reverse=True)
        return all_posts[:max_posts]

# API Routes
@app.post("/api/search-reddit")
async def search_reddit_posts(request: SearchRequest):
    """Search and analyze Reddit posts"""
    try:
        scraper = RedditScraper()
        
        # Search Reddit posts
        posts = scraper.search_reddit(request.query, TARGET_SUBREDDITS, request.max_posts)
        
        if not posts:
            return {"message": "No posts found", "posts": [], "analysis": []}
        
        # Store posts in database
        stored_posts = []
        for post_data in posts:
            reddit_post = RedditPost(**post_data)
            
            # Check if post already exists
            existing = await db.reddit_posts.find_one({"id": reddit_post.id})
            if not existing:
                await db.reddit_posts.insert_one(reddit_post.dict())
            stored_posts.append(reddit_post)
        
        return {
            "message": f"Found {len(stored_posts)} posts",
            "posts": [post.dict() for post in stored_posts],
            "query": request.query
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-posts")
async def analyze_posts(post_ids: List[str]):
    """Analyze posts for relevance and extract insights"""
    try:
        claude_chat = await get_claude_chat()
        analyses = []
        
        for post_id in post_ids:
            # Get post from database
            post = await db.reddit_posts.find_one({"id": post_id})
            if not post:
                continue
                
            # Check if analysis already exists
            existing_analysis = await db.post_analyses.find_one({"post_id": post_id})
            if existing_analysis:
                analyses.append(existing_analysis)
                continue
            
            # Prepare analysis prompt
            analysis_prompt = f"""Analyze this Reddit post for relevance to Eon Health:

Title: {post['title']}
Content: {post['content'][:1000]}...
Subreddit: r/{post['subreddit']}
Upvotes: {post['upvotes']}
Comments: {post['comments_count']}

Please provide:
1. Relevance score (0-100) - how relevant this post is to Eon Health's business
2. Key takeaways (3-5 bullet points)
3. Suggested response/comment we could make (if relevant)
4. Community targeting insights

Format your response as JSON:
{
  "relevance_score": 0-100,
  "takeaways": ["takeaway1", "takeaway2", ...],
  "suggested_response": "suggested comment text",
  "targeting_insights": "insights about this community"
}"""

            try:
                # Get Claude analysis
                message = UserMessage(text=analysis_prompt)
                response = await claude_chat.send_message(message)
                
                # Parse response
                response_text = response.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3].strip()
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3].strip()
                
                analysis_data = json.loads(response_text)
                
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
                
            except Exception as e:
                print(f"Error analyzing post {post_id}: {e}")
                continue
                
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
        
        # Get corresponding posts
        post_ids = [analysis['post_id'] for analysis in analyses]
        posts = await db.reddit_posts.find(
            {"id": {"$in": post_ids}}
        ).to_list(length=None)
        
        # Create posts lookup
        posts_lookup = {post['id']: post for post in posts}
        
        # Prepare trend synthesis prompt
        synthesis_prompt = f"""Based on these {len(analyses)} highly relevant Reddit posts about health/longevity/AI, synthesize key trends and insights for Eon Health:

POSTS ANALYSIS:
"""
        
        for analysis in analyses[:10]:  # Limit to top 10 for prompt length
            post = posts_lookup.get(analysis['post_id'], {})
            synthesis_prompt += f"""
Post: {post.get('title', 'Unknown')} (r/{post.get('subreddit', 'unknown')})
Relevance: {analysis['relevance_score']}/100
Takeaways: {', '.join(analysis['takeaways'])}
---
"""
        
        synthesis_prompt += f"""

Please provide:
1. Key trends (5-7 major themes across these posts)
2. Community insights by subreddit
3. Strategic recommendations for Eon Health

Format as JSON:
{
  "key_trends": ["trend1", "trend2", ...],
  "community_insights": {
    "r/longevity": "insights about this community",
    "r/Biohackers": "insights about this community"
  },
  "suggested_strategies": ["strategy1", "strategy2", ...]
}"""

        # Get Claude synthesis
        claude_chat = await get_claude_chat()
        message = UserMessage(text=synthesis_prompt)
        response = await claude_chat.send_message(message)
        
        # Parse response
        response_text = response.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith('```'):
            response_text = response_text[3:-3].strip()
            
        synthesis_data = json.loads(response_text)
        
        # Create trend synthesis
        trend_synthesis = TrendSynthesis(
            query=query,
            posts_analyzed=len(analyses),
            key_trends=synthesis_data.get('key_trends', []),
            community_insights=synthesis_data.get('community_insights', {}),
            suggested_strategies=synthesis_data.get('suggested_strategies', [])
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
        posts = await db.reddit_posts.find().sort("scraped_at", -1).limit(limit).to_list(length=None)
        
        # Get analyses
        post_ids = [post['id'] for post in posts]
        analyses = await db.post_analyses.find(
            {"post_id": {"$in": post_ids}}
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
        trends = await db.trend_syntheses.find().sort("created_at", -1).limit(limit).to_list(length=None)
        return {"trends": trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)