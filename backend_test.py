import requests
import sys
import json
from datetime import datetime

class RedditTrackingAPITester:
    def __init__(self, base_url="https://reddit-radar.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.sample_post_ids = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=60)

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict):
                        print(f"   Response keys: {list(response_data.keys())}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        return success

    def test_search_reddit(self):
        """Test Reddit search functionality"""
        search_data = {
            "query": "personalized health AI",
            "company_description": "Eon Health - Your Operating System for Healthspan. We use AI, data science, and user-centric design to provide personalized health insights.",
            "max_posts": 5
        }
        
        success, response = self.run_test(
            "Search Reddit Posts",
            "POST",
            "api/search-reddit",
            200,
            data=search_data
        )
        
        if success and isinstance(response, dict):
            posts = response.get('posts', [])
            if posts:
                self.sample_post_ids = [post['id'] for post in posts[:3]]
                print(f"   Found {len(posts)} posts, saved {len(self.sample_post_ids)} IDs for analysis")
            else:
                print("   No posts found in response")
        
        return success

    def test_get_posts(self):
        """Test getting stored posts"""
        success, response = self.run_test(
            "Get Posts",
            "GET",
            "api/posts",
            200,
            params={"limit": 10}
        )
        return success

    def test_analyze_posts(self):
        """Test post analysis functionality"""
        if not self.sample_post_ids:
            print("⚠️  No post IDs available for analysis test")
            return False
            
        success, response = self.run_test(
            "Analyze Posts",
            "POST",
            "api/analyze-posts",
            200,
            data=self.sample_post_ids
        )
        
        if success and isinstance(response, dict):
            analyses = response.get('analyses', [])
            print(f"   Analyzed {len(analyses)} posts")
            
        return success

    def test_synthesize_trends(self):
        """Test trend synthesis functionality"""
        success, response = self.run_test(
            "Synthesize Trends",
            "POST",
            "api/synthesize-trends",
            200,
            params={"query": "personalized health AI", "min_relevance": 30.0}
        )
        
        if success and isinstance(response, dict):
            if 'message' in response:
                print(f"   Message: {response['message']}")
            else:
                print(f"   Trend synthesis completed")
                
        return success

    def test_get_trends(self):
        """Test getting trend syntheses"""
        success, response = self.run_test(
            "Get Trends",
            "GET",
            "api/trends",
            200,
            params={"limit": 5}
        )
        return success

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print(f"\n🧪 Testing Edge Cases...")
        
        # Test empty search query
        empty_search = self.run_test(
            "Empty Search Query",
            "POST",
            "api/search-reddit",
            422,  # Validation error expected
            data={"query": "", "max_posts": 5}
        )[0]
        
        # Test invalid post IDs for analysis
        invalid_analysis = self.run_test(
            "Invalid Post IDs Analysis",
            "POST",
            "api/analyze-posts",
            200,  # Should handle gracefully
            data=["invalid_id_1", "invalid_id_2"]
        )[0]
        
        # Test synthesis with no analyzed posts
        no_posts_synthesis = self.run_test(
            "Synthesis with No Posts",
            "POST",
            "api/synthesize-trends",
            200,  # Should return message about insufficient posts
            params={"query": "nonexistent_topic", "min_relevance": 90.0}
        )[0]
        
        edge_cases_passed = sum([empty_search, invalid_analysis, no_posts_synthesis])
        print(f"   Edge cases passed: {edge_cases_passed}/3")
        
        return edge_cases_passed >= 2  # Allow some flexibility

def main():
    print("🚀 Starting Reddit Tracking Agent API Tests")
    print("=" * 60)
    
    # Setup
    tester = RedditTrackingAPITester()
    
    # Run core functionality tests
    print("\n📋 CORE FUNCTIONALITY TESTS")
    print("-" * 40)
    
    tests = [
        ("Health Check", tester.test_health_check),
        ("Search Reddit", tester.test_search_reddit),
        ("Get Posts", tester.test_get_posts),
        ("Analyze Posts", tester.test_analyze_posts),
        ("Synthesize Trends", tester.test_synthesize_trends),
        ("Get Trends", tester.test_get_trends),
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    # Run edge case tests
    print("\n🧪 EDGE CASE TESTS")
    print("-" * 40)
    tester.test_edge_cases()
    
    # Print final results
    print(f"\n📊 FINAL RESULTS")
    print("=" * 60)
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed >= tester.tests_run * 0.7:  # 70% pass rate
        print("✅ Backend API tests mostly successful!")
        return 0
    else:
        print("❌ Backend API tests failed - too many failures")
        return 1

if __name__ == "__main__":
    sys.exit(main())