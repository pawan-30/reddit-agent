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

class AnalyzeRequest(BaseModel):
    post_ids: List[str]
    company_description: str = ""

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

# Enhanced analysis function for eon.health
def analyze_post_for_eon_health(post, company_description=""):
    """Advanced analysis function tailored for eon.health's Space-Time Health OS platform"""
    
    title_lower = post['title'].lower()
    content_lower = post['content'].lower()
    combined_text = f"{title_lower} {content_lower}"
    
    # Parse company description for additional context
    company_keywords = []
    company_focus_areas = []
    
    if company_description:
        company_lower = company_description.lower()
        
        # Enhanced focus area detection for comprehensive descriptions
        focus_indicators = {
            'ai_focus': ['ai', 'artificial intelligence', 'machine learning', 'algorithms', 'predictive', 'correlation engine', 'analytics'],
            'personalization_focus': ['personalized', 'personalization', 'individualized', 'custom', 'tailored', 'individual', 'personal data'],
            'device_focus': ['wearable', 'device', 'sensor', 'tracking', 'monitoring', 'integration', 'biometric'],
            'longevity_focus': ['longevity', 'aging', 'healthspan', 'lifespan', 'anti-aging', 'age', 'functional age'],
            'prevention_focus': ['prevention', 'preventive', 'proactive', 'early detection', 'predictive', 'outcomes'],
            'data_focus': ['data', 'analytics', 'correlation', 'patterns', 'metrics', 'analysis', 'insights', 'time series'],
            'holistic_focus': ['comprehensive', 'holistic', 'multi-dimensional', 'interconnected', 'orchestration', 'pillars', 'framework'],
            'social_focus': ['social', 'community', 'connection', 'collective', 'digital siblings', 'hive', 'sharing'],
            'recovery_focus': ['recovery', 'sleep', 'rest', 'restoration', 'rem', 'deep sleep'],
            'nutrition_focus': ['nutrition', 'meal', 'food', 'nutrient', 'diet', 'eating'],
            'movement_focus': ['movement', 'exercise', 'workout', 'fitness', 'activity', 'strength'],
            'cognition_focus': ['cognition', 'cognitive', 'brain', 'mental', 'meditation', 'mindfulness']
        }
        
        # Check for focus areas based on keyword presence
        for focus_area, indicators in focus_indicators.items():
            if any(indicator in company_lower for indicator in indicators):
                company_focus_areas.append(focus_area)
        
        # Extract meaningful keywords (longer than 4 characters, excluding common words)
        common_words = {'that', 'with', 'from', 'they', 'have', 'this', 'will', 'your', 'what', 'when', 'where', 'which', 'their', 'there', 'these', 'those'}
        company_words = company_lower.split()
        company_keywords = [word.strip('.,!?;:()[]{}') for word in company_words 
                          if len(word) > 4 and word.lower() not in common_words]
    
    # Eon.health specific keyword categories with weights
    keyword_categories = {
        'space_time_health': {
            'keywords': ['longitudinal', 'temporal', 'time series', 'historical data', 'predictive', 'forecasting', 'patterns over time', 'health trajectory', 'progression', 'evolution'],
            'weight': 25,
            'description': 'Space-Time Health OS concepts'
        },
        'ai_personalization': {
            'keywords': ['personalized', 'individualized', 'custom', 'tailored', 'ai', 'machine learning', 'algorithm', 'artificial intelligence', 'predictive analytics', 'data science'],
            'weight': 20,
            'description': 'AI-driven personalization'
        },
        'multi_dimensional_health': {
            'keywords': ['holistic', 'comprehensive', 'integrated', 'multi-factor', 'interconnected', 'systems approach', 'network', 'orchestration', 'coordination'],
            'weight': 18,
            'description': 'Multi-dimensional health orchestration'
        },
        'biometric_integration': {
            'keywords': ['wearable', 'sensor', 'biomarker', 'biometric', 'continuous monitoring', 'real-time', 'data integration', 'quantified self', 'tracking'],
            'weight': 15,
            'description': 'Biometric data integration'
        },
        'longevity_healthspan': {
            'keywords': ['longevity', 'healthspan', 'aging', 'lifespan', 'anti-aging', 'life extension', 'healthy aging', 'age reversal', 'cellular health'],
            'weight': 15,
            'description': 'Longevity and healthspan focus'
        },
        'preventive_optimization': {
            'keywords': ['prevention', 'optimization', 'enhancement', 'improvement', 'proactive', 'preventive medicine', 'wellness optimization', 'performance'],
            'weight': 12,
            'description': 'Preventive health optimization'
        }
    }
    
    # Calculate relevance score and identify key themes
    relevance_score = 0
    detected_themes = []
    theme_details = {}
    
    for category, data in keyword_categories.items():
        category_score = 0
        matched_keywords = []
        
        for keyword in data['keywords']:
            if keyword in combined_text:
                # Higher weight for title matches
                title_matches = title_lower.count(keyword)
                content_matches = content_lower.count(keyword)
                
                keyword_score = (title_matches * 2 + content_matches) * data['weight']
                category_score += keyword_score
                
                if keyword_score > 0:
                    matched_keywords.append(keyword)
        
        if category_score > 0:
            relevance_score += min(category_score, data['weight'] * 2)  # Cap per category
            detected_themes.append(category)
            theme_details[category] = {
                'score': category_score,
                'keywords': matched_keywords,
                'description': data['description']
            }
    
    # Company-specific relevance boost
    company_boost = 0
    if company_description:
        # Boost relevance if post content aligns with company focus areas
        focus_theme_mapping = {
            'ai_focus': ['ai_personalization', 'space_time_health'],
            'personalization_focus': ['ai_personalization', 'multi_dimensional_health'],
            'device_focus': ['biometric_integration'],
            'longevity_focus': ['longevity_healthspan', 'preventive_optimization'],
            'prevention_focus': ['preventive_optimization'],
            'data_focus': ['space_time_health', 'biometric_integration'],
            'holistic_focus': ['multi_dimensional_health', 'space_time_health'],
            'social_focus': ['multi_dimensional_health'],
            'recovery_focus': ['longevity_healthspan', 'preventive_optimization'],
            'nutrition_focus': ['ai_personalization', 'preventive_optimization'],
            'movement_focus': ['biometric_integration', 'preventive_optimization'],
            'cognition_focus': ['ai_personalization', 'multi_dimensional_health']
        }
        
        for focus_area in company_focus_areas:
            if focus_area in focus_theme_mapping:
                for theme in focus_theme_mapping[focus_area]:
                    if theme in detected_themes:
                        company_boost += 12  # Boost per matching theme
        
        # Additional boost for company-specific keywords in post (limited to prevent over-boosting)
        keyword_matches = 0
        for keyword in company_keywords[:20]:  # Limit to first 20 keywords to prevent excessive boosting
            if keyword in combined_text:
                keyword_matches += 1
        
        company_boost += min(keyword_matches * 2, 20)  # Max 20 points from keyword matching
        
        relevance_score += min(company_boost, 40)  # Increased cap for comprehensive descriptions
    
    # Engagement multiplier based on community activity
    engagement_multiplier = min(1.5, 1 + (post['upvotes'] / 1000) + (post['comments_count'] / 100))
    relevance_score = min(100, relevance_score * engagement_multiplier)
    
    # Generate sophisticated takeaways based on detected themes
    takeaways = generate_eon_health_takeaways(post, detected_themes, theme_details, company_description, company_focus_areas)
    
    # Generate targeted response based on themes and community
    suggested_response = generate_eon_health_response(post, detected_themes, theme_details, company_description, company_focus_areas)
    
    # Generate community-specific targeting insights
    targeting_insights = generate_targeting_insights(post, detected_themes, theme_details, company_description, company_focus_areas)
    
    return {
        "relevance_score": round(relevance_score, 1),
        "takeaways": takeaways,
        "suggested_response": suggested_response,
        "targeting_insights": targeting_insights,
        "detected_themes": detected_themes,
        "theme_analysis": theme_details
    }

def generate_eon_health_takeaways(post, themes, theme_details, company_description="", company_focus_areas=[]):
    """Generate sophisticated takeaways aligned with eon.health's positioning"""
    takeaways = []
    
    # Theme-specific insights
    if 'space_time_health' in themes:
        takeaways.append("Discussion aligns with eon.health's Space-Time Health OS approach - community recognizes importance of temporal health patterns and predictive analytics")
    
    if 'ai_personalization' in themes:
        takeaways.append("Strong alignment with eon.health's AI-driven personalization - community actively seeks individualized health solutions beyond one-size-fits-all approaches")
    
    if 'multi_dimensional_health' in themes:
        takeaways.append("Community demonstrates understanding of health as interconnected system - perfect fit for eon.health's comprehensive orchestration platform")
    
    if 'biometric_integration' in themes:
        takeaways.append("Active interest in continuous health monitoring and data integration - validates eon.health's wearable-centric approach")
    
    if 'longevity_healthspan' in themes:
        takeaways.append("Community prioritizes healthspan extension over mere lifespan - directly aligned with eon.health's longevity mission")
    
    if 'preventive_optimization' in themes:
        takeaways.append("Proactive health optimization mindset present - ideal audience for eon.health's preventive intelligence platform")
    
    # Community engagement insights
    engagement_level = "high" if post['upvotes'] > 100 else "moderate" if post['upvotes'] > 20 else "emerging"
    takeaways.append(f"r/{post['subreddit']} shows {engagement_level} engagement ({post['upvotes']} upvotes, {post['comments_count']} comments) - indicates receptive audience for advanced health tech")
    
    # Company-specific strategic insights
    if company_description:
        if 'ai_focus' in company_focus_areas and 'ai_personalization' in themes:
            takeaways.append("Strong alignment with company's AI focus - community actively discusses personalized AI solutions")
        if 'personalization_focus' in company_focus_areas and any(theme in themes for theme in ['ai_personalization', 'multi_dimensional_health']):
            takeaways.append("Perfect match for company's personalization mission - community seeks individualized health approaches")
        if 'device_focus' in company_focus_areas and 'biometric_integration' in themes:
            takeaways.append("Excellent opportunity for company's device integration - community actively uses wearable technology")
        if 'longevity_focus' in company_focus_areas and 'longevity_healthspan' in themes:
            takeaways.append("Direct alignment with company's longevity mission - community prioritizes healthspan optimization")
        if 'data_focus' in company_focus_areas and 'space_time_health' in themes:
            takeaways.append("Strong fit for company's data analytics approach - community values temporal health insights")
    
    # Add strategic opportunity insight
    if len(themes) >= 3:
        company_name = "your company" if not company_description else "the company"
        takeaways.append(f"Multi-dimensional health discussion presents opportunity for {company_name} to demonstrate comprehensive platform capabilities")
    elif len(themes) >= 1:
        company_name = "your company" if not company_description else "the company"
        takeaways.append(f"Focused health discussion allows for targeted demonstration of specific {company_name} capabilities")
    
    return takeaways[:6]  # Limit to most relevant takeaways

def generate_eon_health_response(post, themes, theme_details, company_description="", company_focus_areas=[]):
    """Generate sophisticated, theme-aware responses for eon.health"""
    
    subreddit = post['subreddit']
    
    # Base response templates by community
    community_intros = {
        'longevity': "Fascinating insights on longevity optimization!",
        'Biohackers': "Love seeing the biohacking community explore this!",
        'science': "Great to see rigorous scientific discussion here.",
        'QuantifiedSelf': "This quantified approach resonates strongly with our mission.",
        'Futurology': "This future-forward thinking aligns perfectly with our vision.",
        'health': "Important health insights being shared here.",
        'aging': "Critical aging research discussion.",
        'artificial': "Exciting to see AI applications in health being explored.",
        'singularity': "The convergence of AI and health is indeed transformative."
    }
    
    intro = community_intros.get(subreddit, "Really insightful discussion!")
    
    # Theme-specific value propositions (customized based on company description)
    value_props = []
    
    # Use company-specific messaging if available
    company_name = "eon.health"
    if company_description:
        # Extract company name if mentioned
        if "eon.health" in company_description.lower():
            company_name = "eon.health"
        else:
            company_name = "our company"
    
    if 'space_time_health' in themes:
        if 'data_focus' in company_focus_areas:
            value_props.append(f"At {company_name}, we've built what we call a 'Space-Time Health OS' that does exactly this - our advanced data analytics platform analyzes your health patterns across both personal data dimensions and temporal evolution to predict optimal interventions.")
        else:
            value_props.append(f"At {company_name}, we've built what we call a 'Space-Time Health OS' that does exactly this - analyzing your health patterns across both personal data dimensions and temporal evolution to predict optimal interventions.")
    
    if 'ai_personalization' in themes:
        if 'ai_focus' in company_focus_areas:
            value_props.append(f"Our cutting-edge AI platform goes beyond generic recommendations by creating truly individualized health orchestration based on your unique biological signature, lifestyle patterns, and response history.")
        else:
            value_props.append(f"Our AI platform goes beyond generic recommendations by creating truly individualized health orchestration based on your unique biological signature, lifestyle patterns, and response history.")
    
    if 'multi_dimensional_health' in themes:
        if 'personalization_focus' in company_focus_areas:
            value_props.append(f"We've architected our platform as a comprehensive, personalized health operating system that orchestrates the interconnected aspects of nutrition, sleep, exercise, stress, and biomarkers as a unified system tailored to each individual.")
        else:
            value_props.append(f"We've architected our platform as a comprehensive health operating system that orchestrates the interconnected aspects of nutrition, sleep, exercise, stress, and biomarkers as a unified system.")
    
    if 'biometric_integration' in themes:
        if 'device_focus' in company_focus_areas:
            value_props.append(f"Our platform integrates seamlessly with a wide range of wearables and medical devices to provide continuous, real-time health intelligence that evolves with your changing biology.")
        else:
            value_props.append(f"Our platform integrates seamlessly with wearables and lab data to provide continuous, real-time health intelligence that evolves with your changing biology.")
    
    if 'longevity_healthspan' in themes:
        if 'longevity_focus' in company_focus_areas:
            value_props.append(f"Our core mission is extending healthspan through predictive interventions that prevent decline before it starts, rather than just treating symptoms - we're focused on adding healthy years to life.")
        else:
            value_props.append(f"Our focus is specifically on extending healthspan through predictive interventions that prevent decline before it starts, rather than just treating symptoms.")
    
    # Fallback value prop if no specific themes detected
    if not value_props:
        if company_description:
            value_props.append(f"We're building an AI-powered health platform that transforms raw biometric data into actionable, personalized insights aligned with our mission of optimizing human health.")
        else:
            value_props.append("We're building an AI-powered health operating system that transforms raw biometric data into actionable, personalized insights for optimizing healthspan.")
    
    # Community-specific call to action
    cta_options = {
        'longevity': "Would love to hear your thoughts on how predictive health analytics could accelerate longevity research.",
        'Biohackers': "Curious what biohacking experiments you'd want to optimize with predictive AI?",
        'science': "Happy to share more about our research methodology if you're interested in the scientific approach.",
        'QuantifiedSelf': "Would be interested in your perspective on what health metrics matter most for predictive modeling.",
        'Futurology': "What do you think the next breakthrough in personalized health will be?",
        'health': "What aspects of personalized health optimization interest you most?",
        'aging': "How do you think AI could best accelerate healthy aging research?",
        'artificial': "What AI applications in health excite you most?",
        'singularity': "How do you see AI transforming human health optimization?"
    }
    
    cta = cta_options.get(subreddit, "What aspects of personalized health AI interest you most?")
    
    # Combine into cohesive response
    response = f"{intro} {value_props[0]} {cta}"
    
    return response

def generate_targeting_insights(post, themes, theme_details, company_description="", company_focus_areas=[]):
    """Generate sophisticated community targeting insights"""
    
    subreddit = post['subreddit']
    
    # Community-specific insights
    community_profiles = {
        'longevity': "Highly educated, research-oriented community focused on evidence-based life extension. Values scientific rigor and long-term thinking.",
        'Biohackers': "Tech-savvy early adopters interested in self-experimentation and optimization. Willing to try new technologies and approaches.",
        'science': "Academic and research-focused audience that demands peer-reviewed evidence and rigorous methodology.",
        'QuantifiedSelf': "Data-driven individuals who actively track health metrics. Highly receptive to technology-enabled health optimization.",
        'Futurology': "Forward-thinking community interested in emerging technologies and their societal impact. Open to disruptive innovations.",
        'health': "Broad health-conscious audience seeking practical wellness solutions. Mix of consumers and professionals.",
        'aging': "Research-focused community studying aging mechanisms. Values scientific approach to healthy aging.",
        'artificial': "AI enthusiasts interested in practical applications. Technical audience that understands AI capabilities.",
        'singularity': "Technology futurists interested in transformative AI applications. Philosophical and technical discussions."
    }
    
    base_insight = community_profiles.get(subreddit, "Health-interested community with varying levels of technical sophistication.")
    
    # Theme-based targeting recommendations
    targeting_recs = []
    
    if 'space_time_health' in themes:
        targeting_recs.append("Emphasize temporal analytics and predictive capabilities - this community understands the value of longitudinal health data.")
    
    if 'ai_personalization' in themes:
        targeting_recs.append("Lead with AI sophistication and personalization depth - audience appreciates technical complexity.")
    
    if 'multi_dimensional_health' in themes:
        targeting_recs.append("Highlight systems thinking and comprehensive integration - community values holistic approaches.")
    
    if 'biometric_integration' in themes:
        targeting_recs.append("Focus on data integration capabilities and continuous monitoring - audience actively uses health tech.")
    
    if 'longevity_healthspan' in themes:
        targeting_recs.append("Position as longevity-focused platform with preventive approach - aligns with community priorities.")
    
    # Engagement strategy
    engagement_level = post['upvotes']
    if engagement_level > 200:
        engagement_note = "High-engagement post indicates strong community interest - ideal for detailed technical discussion."
    elif engagement_level > 50:
        engagement_note = "Moderate engagement suggests receptive audience - good opportunity for educational content."
    else:
        engagement_note = "Emerging discussion - opportunity to provide valuable insights and establish thought leadership."
    
    # Company-specific targeting recommendations
    if company_description and company_focus_areas:
        company_recs = []
        if 'ai_focus' in company_focus_areas:
            company_recs.append("Emphasize AI sophistication and technical capabilities - aligns with company's AI focus.")
        if 'personalization_focus' in company_focus_areas:
            company_recs.append("Highlight personalization depth and individual customization - matches company's core mission.")
        if 'device_focus' in company_focus_areas:
            company_recs.append("Showcase device integration and wearable compatibility - leverages company's hardware expertise.")
        if 'longevity_focus' in company_focus_areas:
            company_recs.append("Position as longevity-focused solution with preventive approach - aligns with company's mission.")
        if 'data_focus' in company_focus_areas:
            company_recs.append("Lead with data analytics and insights capabilities - matches company's data expertise.")
        
        targeting_recs.extend(company_recs)
    
    # Combine insights
    full_insight = f"{base_insight} {' '.join(targeting_recs)} {engagement_note}"
    
    return full_insight

def synthesize_trends_for_eon_health(query, analyses):
    """Generate sophisticated trend synthesis aligned with eon.health's Space-Time Health OS positioning"""
    
    # Analyze theme distribution across posts
    theme_frequency = {}
    community_themes = {}
    high_relevance_posts = [a for a in analyses if a.get('relevance_score', 0) >= 70]
    
    for analysis in analyses:
        # Extract themes from analysis if available
        themes = analysis.get('detected_themes', [])
        for theme in themes:
            theme_frequency[theme] = theme_frequency.get(theme, 0) + 1
        
        # Track community-specific themes
        post_id = analysis.get('post_id')
        # Note: In a real implementation, you'd fetch the post to get subreddit
        # For now, we'll use mock community data
    
    # Generate sophisticated key trends based on theme analysis
    key_trends = generate_key_trends(theme_frequency, len(analyses), query)
    
    # Generate community insights based on eon.health positioning
    community_insights = generate_community_insights(analyses)
    
    # Generate strategic recommendations for eon.health
    suggested_strategies = generate_strategic_recommendations(theme_frequency, community_insights, query)
    
    return TrendSynthesis(
        query=query,
        posts_analyzed=len(analyses),
        key_trends=key_trends,
        community_insights=community_insights,
        suggested_strategies=suggested_strategies
    )

def generate_key_trends(theme_frequency, total_posts, query):
    """Generate sophisticated trend insights based on theme analysis"""
    trends = []
    
    # Calculate theme percentages
    theme_percentages = {theme: (count/total_posts)*100 for theme, count in theme_frequency.items()}
    
    # Space-Time Health OS trends
    if theme_percentages.get('space_time_health', 0) > 20:
        trends.append(f"Strong momentum toward temporal health analytics - {theme_percentages['space_time_health']:.0f}% of discussions recognize the importance of longitudinal health patterns, validating eon.health's Space-Time Health OS approach")
    
    # AI Personalization trends
    if theme_percentages.get('ai_personalization', 0) > 30:
        trends.append(f"AI-driven personalization is becoming mainstream expectation - {theme_percentages['ai_personalization']:.0f}% of conversations demand individualized solutions beyond generic health advice")
    
    # Multi-dimensional health trends
    if theme_percentages.get('multi_dimensional_health', 0) > 25:
        trends.append(f"Systems thinking in health is gaining traction - {theme_percentages['multi_dimensional_health']:.0f}% of discussions recognize health as interconnected network rather than isolated metrics")
    
    # Biometric integration trends
    if theme_percentages.get('biometric_integration', 0) > 35:
        trends.append(f"Wearable-centric health monitoring is now expected standard - {theme_percentages['biometric_integration']:.0f}% of conversations assume continuous biometric integration")
    
    # Longevity trends
    if theme_percentages.get('longevity_healthspan', 0) > 40:
        trends.append(f"Healthspan optimization prioritized over lifespan extension - {theme_percentages['longevity_healthspan']:.0f}% of longevity discussions focus on quality of life rather than mere longevity")
    
    # Preventive optimization trends
    if theme_percentages.get('preventive_optimization', 0) > 30:
        trends.append(f"Proactive health optimization becoming dominant paradigm - {theme_percentages['preventive_optimization']:.0f}% of discussions emphasize prevention over treatment")
    
    # Add meta-trends based on overall analysis
    if len(theme_frequency) >= 4:
        trends.append("Multi-dimensional health conversations indicate market readiness for comprehensive health orchestration platforms like eon.health's Space-Time Health OS")
    
    if total_posts >= 10:
        trends.append(f"Sustained community engagement around '{query}' ({total_posts} analyzed posts) suggests strong market demand for advanced health optimization solutions")
    
    return trends[:6]  # Return top 6 trends

def generate_community_insights(analyses):
    """Generate sophisticated community insights for eon.health positioning"""
    
    # Mock community analysis - in real implementation, would analyze actual post subreddits
    insights = {
        "r/longevity": "Premium audience for eon.health's healthspan extension mission - highly educated, research-oriented community that values evidence-based approaches to aging optimization. Strong alignment with Space-Time Health OS temporal analytics.",
        
        "r/Biohackers": "Early adopter community ideal for eon.health beta testing and feedback - tech-savvy users who actively experiment with health optimization tools. High receptivity to AI-driven personalization features.",
        
        "r/QuantifiedSelf": "Data-driven health enthusiasts who represent eon.health's core user persona - already tracking multiple health metrics and seeking sophisticated analytics. Perfect fit for comprehensive health orchestration platform.",
        
        "r/science": "Credibility-building community for eon.health's research validation - academic audience that can provide scientific legitimacy and peer review. Critical for establishing evidence-based positioning.",
        
        "r/Futurology": "Vision-aligned community for eon.health's transformative health technology narrative - forward-thinking audience receptive to paradigm-shifting health solutions. Ideal for thought leadership content.",
        
        "r/artificial": "Technical validation community for eon.health's AI capabilities - understands machine learning sophistication and can appreciate advanced algorithmic approaches to health optimization."
    }
    
    return insights

def generate_strategic_recommendations(theme_frequency, community_insights, query):
    """Generate sophisticated strategic recommendations for eon.health market positioning"""
    
    strategies = []
    
    # Theme-based strategies
    if theme_frequency.get('space_time_health', 0) > 0:
        strategies.append("Lead with 'Space-Time Health OS' positioning in longevity and quantified self communities - unique temporal analytics approach differentiates from point-in-time health apps")
    
    if theme_frequency.get('ai_personalization', 0) > 0:
        strategies.append("Emphasize AI sophistication and personalization depth in technical communities - demonstrate advanced algorithmic capabilities beyond basic recommendation engines")
    
    if theme_frequency.get('multi_dimensional_health', 0) > 0:
        strategies.append("Position as comprehensive health orchestration platform rather than single-purpose app - highlight systems integration capabilities")
    
    if theme_frequency.get('biometric_integration', 0) > 0:
        strategies.append("Showcase seamless wearable integration and continuous monitoring capabilities - demonstrate superior data integration compared to fragmented solutions")
    
    # Community-specific strategies
    strategies.append("Establish thought leadership in r/longevity through research-backed content on healthspan optimization and predictive health analytics")
    
    strategies.append("Engage r/Biohackers community with beta testing opportunities and advanced feature previews - leverage their experimentation mindset for product development feedback")
    
    strategies.append("Build credibility in r/science through peer-reviewed research publications and transparent methodology sharing")
    
    strategies.append("Create educational content for r/QuantifiedSelf demonstrating how eon.health transforms raw data into actionable insights")
    
    # Market positioning strategies
    if len(theme_frequency) >= 3:
        strategies.append("Position eon.health as the 'health operating system' that unifies fragmented health tech ecosystem - emphasize comprehensive orchestration over point solutions")
    
    strategies.append("Develop case studies showcasing predictive health interventions and measurable healthspan improvements to validate Space-Time Health OS approach")
    
    return strategies[:8]  # Return top 8 strategies

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
        # return {
        #     "message": f"Demo mode: Returning demonstration posts for '{request.query}'"}
        scraper = RedditScraper()
        print("hi")                                       
    
        # Search Reddit posts
        posts = scraper.search_reddit(request.query, TARGET_SUBREDDITS, request.max_posts)
        print("bye")
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
async def analyze_posts(request: AnalyzeRequest):
    """Analyze posts for relevance and extract insights"""
    try:
        analyses = []
        
        for post_id in request.post_ids:
            # Get post from database
            post = await db.reddit_posts.find_one({"id": post_id})
            if not post:
                continue
                
            # Check if analysis already exists with same company description
            # We'll re-analyze if company description changed
            existing_analysis = await db.post_analyses.find_one({"post_id": post_id}, {"_id": 0})
            
            # Enhanced analysis for eon.health with company description
            analysis_data = analyze_post_for_eon_health(post, request.company_description)
            
            # Create analysis object
            analysis = PostAnalysis(
                post_id=post_id,
                relevance_score=float(analysis_data.get('relevance_score', 0)),
                takeaways=analysis_data.get('takeaways', []),
                suggested_response=analysis_data.get('suggested_response', ''),
                targeting_insights=analysis_data.get('targeting_insights', '')
            )
            
            # Store or update analysis
            await db.post_analyses.replace_one(
                {"post_id": post_id}, 
                analysis.dict(), 
                upsert=True
            )
            analyses.append(analysis.dict())
                
        return {"analyses": analyses}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/synthesize-trends")
async def synthesize_trends(query: str = Query(...), min_relevance: float = Query(50.0)):
    """Synthesize trends from analyzed posts"""
    try:
        # Get high-relevance analyses
        analyses = await db.post_analyses.find(
            {"relevance_score": {"$gte": min_relevance}}
        ).to_list(length=None)
        
        print(f"Found {len(analyses)} analyses with relevance >= {min_relevance}")
        
        if len(analyses) < 2:
            # If not enough high-relevance posts, try with lower threshold
            all_analyses = await db.post_analyses.find({}).to_list(length=None)
            print(f"Total analyses in database: {len(all_analyses)}")
            
            if len(all_analyses) >= 2:
                # Use all available analyses for trend synthesis
                analyses = all_analyses
                print(f"Using all {len(analyses)} analyses for trend synthesis")
            else:
                return {"message": f"Not enough analyzed posts for trend analysis. Found {len(all_analyses)} analyzed posts, need at least 2."}
        
        # Enhanced trend synthesis for eon.health
        trend_synthesis = synthesize_trends_for_eon_health(query, analyses)
        
        # Store synthesis
        await db.trend_syntheses.insert_one(trend_synthesis.dict())
        
        return trend_synthesis.dict()
        
    except Exception as e:
        print(f"Error in synthesize_trends: {e}")
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