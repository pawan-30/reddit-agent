#!/usr/bin/env python3
"""
Test script for full workflow: search -> analyze -> synthesize trends
"""

import requests
import json
import time

BACKEND_URL = "http://localhost:8001"

def test_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/health")
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except:
        print("❌ Backend is not running")
        return False

def test_search_reddit():
    """Test Reddit search functionality"""
    print("\n=== Testing Reddit Search ===")
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/search-reddit", json={
            "query": "personalized health",
            "company_description": "eon.health test",
            "max_posts": 5
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search successful: {data.get('message', 'No message')}")
            posts = data.get('posts', [])
            print(f"Found {len(posts)} posts")
            return posts
        else:
            print(f"❌ Search failed: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Search error: {e}")
        return []

def test_analyze_posts(posts):
    """Test post analysis functionality"""
    print("\n=== Testing Post Analysis ===")
    
    if not posts:
        print("❌ No posts to analyze")
        return False
    
    try:
        post_ids = [post['id'] for post in posts[:3]]  # Analyze first 3 posts
        print(f"Analyzing posts: {post_ids}")
        
        response = requests.post(f"{BACKEND_URL}/api/analyze-posts", json=post_ids)
        
        if response.status_code == 200:
            data = response.json()
            analyses = data.get('analyses', [])
            print(f"✅ Analysis successful: {len(analyses)} posts analyzed")
            
            for analysis in analyses:
                print(f"  Post {analysis['post_id']}: {analysis['relevance_score']}% relevance")
            
            return len(analyses) > 0
        else:
            print(f"❌ Analysis failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False

def test_synthesize_trends():
    """Test trend synthesis functionality"""
    print("\n=== Testing Trend Synthesis ===")
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/synthesize-trends", params={
            "query": "personalized health",
            "min_relevance": 0  # Use low threshold to ensure we get results
        })
        
        if response.status_code == 200:
            data = response.json()
            
            if 'message' in data:
                print(f"⚠️  Synthesis message: {data['message']}")
                return False
            else:
                print("✅ Trend synthesis successful!")
                print(f"Query: {data.get('query')}")
                print(f"Posts analyzed: {data.get('posts_analyzed')}")
                print(f"Key trends: {len(data.get('key_trends', []))}")
                print(f"Community insights: {len(data.get('community_insights', {}))}")
                print(f"Strategies: {len(data.get('suggested_strategies', []))}")
                return True
        else:
            print(f"❌ Synthesis failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Synthesis error: {e}")
        return False

def test_get_trends():
    """Test getting stored trends"""
    print("\n=== Testing Get Trends ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/trends")
        
        if response.status_code == 200:
            data = response.json()
            trends = data.get('trends', [])
            print(f"✅ Retrieved {len(trends)} stored trends")
            
            for i, trend in enumerate(trends):
                print(f"  Trend {i+1}: {trend.get('query')} ({trend.get('posts_analyzed')} posts)")
            
            return len(trends) > 0
        else:
            print(f"❌ Get trends failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Get trends error: {e}")
        return False

def main():
    """Run full workflow test"""
    print("=== Full Workflow Test ===")
    
    if not test_health():
        print("\nPlease start the backend server first: cd backend && python server.py")
        return
    
    # Step 1: Search for posts
    posts = test_search_reddit()
    
    # Step 2: Analyze posts
    if posts:
        analysis_success = test_analyze_posts(posts)
        
        # Step 3: Synthesize trends
        if analysis_success:
            synthesis_success = test_synthesize_trends()
            
            # Step 4: Get trends
            if synthesis_success:
                test_get_trends()
                print("\n✅ Full workflow completed successfully!")
            else:
                print("\n❌ Workflow failed at trend synthesis")
        else:
            print("\n❌ Workflow failed at post analysis")
    else:
        print("\n❌ Workflow failed at Reddit search")

if __name__ == "__main__":
    main()