#!/usr/bin/env python3
"""
Test script for synthesize trends functionality
"""

import requests
import json

BACKEND_URL = "http://localhost:8001"

def test_synthesize_trends():
    """Test the synthesize trends endpoint"""
    
    print("=== Testing Synthesize Trends Endpoint ===\n")
    
    # Test parameters
    query = "personalized health"
    min_relevance = 50.0
    
    try:
        # Make POST request to synthesize trends
        url = f"{BACKEND_URL}/api/synthesize-trends"
        params = {
            "query": query,
            "min_relevance": min_relevance
        }
        
        print(f"Making POST request to: {url}")
        print(f"Parameters: {params}")
        
        response = requests.post(url, params=params)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response data:")
            print(json.dumps(data, indent=2))
        else:
            print("❌ Error response:")
            print(f"Status: {response.status_code}")
            print(f"Text: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure backend server is running on http://localhost:8001")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health_endpoint():
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

if __name__ == "__main__":
    print("Testing backend connectivity...")
    if test_health_endpoint():
        print()
        test_synthesize_trends()
    else:
        print("Please start the backend server first: cd backend && python server.py")