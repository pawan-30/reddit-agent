#!/usr/bin/env python3
"""
Test script for enhanced eon.health analysis capabilities
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from server import analyze_post_for_eon_health, synthesize_trends_for_eon_health

def test_enhanced_analysis():
    """Test the enhanced analysis with sample posts"""
    
    # Sample posts that should trigger different themes
    test_posts = [
        {
            'id': 'test1',
            'title': 'AI-powered personalized nutrition based on continuous glucose monitoring and genetic data',
            'content': 'New research shows that personalized nutrition recommendations based on individual genetic markers, microbiome analysis, and continuous glucose monitoring can improve metabolic health outcomes by 40%. The AI system analyzes temporal patterns in blood glucose response to different foods and creates individualized meal plans. This longitudinal approach considers how your body changes over time.',
            'subreddit': 'longevity',
            'author': 'health_researcher',
            'upvotes': 245,
            'comments_count': 67,
            'url': 'https://reddit.com/test1'
        },
        {
            'id': 'test2', 
            'title': 'Comprehensive biohacking setup: integrating wearables, lab tests, and predictive analytics',
            'content': 'My complete biohacking stack includes continuous heart rate monitoring, sleep tracking, HRV analysis, monthly blood panels, and a custom AI system that predicts optimal intervention timing. The key is looking at health as an interconnected system rather than isolated metrics. The predictive algorithms help me optimize interventions before problems arise.',
            'subreddit': 'Biohackers',
            'author': 'quantified_biohacker',
            'upvotes': 156,
            'comments_count': 43,
            'url': 'https://reddit.com/test2'
        },
        {
            'id': 'test3',
            'title': 'Longitudinal health data analysis reveals aging patterns decades before symptoms',
            'content': 'Fascinating study analyzing 20 years of health data from 10,000 participants. Machine learning algorithms identified subtle patterns in biomarkers that predict age-related decline 15-20 years before clinical symptoms appear. This temporal approach to health could revolutionize preventive medicine.',
            'subreddit': 'science',
            'author': 'aging_researcher',
            'upvotes': 892,
            'comments_count': 234,
            'url': 'https://reddit.com/test3'
        }
    ]
    
    print("=== Testing Enhanced Eon.Health Analysis ===\n")
    
    analyses = []
    for post in test_posts:
        print(f"Analyzing: {post['title'][:60]}...")
        analysis = analyze_post_for_eon_health(post)
        analyses.append(analysis)
        
        print(f"Relevance Score: {analysis['relevance_score']}")
        print(f"Detected Themes: {', '.join(analysis['detected_themes'])}")
        print(f"Key Takeaway: {analysis['takeaways'][0]}")
        print(f"Response Strategy: {analysis['suggested_response'][:100]}...")
        print("-" * 80)
    
    # Test trend synthesis
    print("\n=== Testing Trend Synthesis ===\n")
    
    # Create mock analyses for trend synthesis
    mock_analyses = []
    for i, analysis in enumerate(analyses):
        mock_analysis = {
            'post_id': f'test{i+1}',
            'relevance_score': analysis['relevance_score'],
            'detected_themes': analysis['detected_themes'],
            'takeaways': analysis['takeaways']
        }
        mock_analyses.append(mock_analysis)
    
    trend_synthesis = synthesize_trends_for_eon_health("personalized health AI", mock_analyses)
    
    print(f"Query: {trend_synthesis.query}")
    print(f"Posts Analyzed: {trend_synthesis.posts_analyzed}")
    print("\nKey Trends:")
    for i, trend in enumerate(trend_synthesis.key_trends, 1):
        print(f"{i}. {trend}")
    
    print("\nCommunity Insights:")
    for community, insight in trend_synthesis.community_insights.items():
        print(f"{community}: {insight[:100]}...")
    
    print("\nStrategic Recommendations:")
    for i, strategy in enumerate(trend_synthesis.suggested_strategies, 1):
        print(f"{i}. {strategy}")

if __name__ == "__main__":
    test_enhanced_analysis()