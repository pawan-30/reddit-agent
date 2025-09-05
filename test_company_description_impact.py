#!/usr/bin/env python3
"""
Test script to demonstrate how company description affects analysis results
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from server import analyze_post_for_eon_health

def test_company_description_impact():
    """Test how different company descriptions affect analysis results"""
    
    # Sample post about AI-powered health monitoring
    test_post = {
        'id': 'test_company_impact',
        'title': 'AI-powered wearable device predicts health issues 48 hours before symptoms appear',
        'content': 'New research shows that machine learning algorithms analyzing continuous biometric data from wearables can predict cardiovascular events, infections, and metabolic disorders up to 48 hours before clinical symptoms manifest. The system uses personalized baselines and temporal pattern recognition to identify subtle deviations that indicate impending health issues.',
        'subreddit': 'Biohackers',
        'author': 'health_tech_researcher',
        'upvotes': 342,
        'comments_count': 87,
        'url': 'https://reddit.com/test_company_impact'
    }
    
    # Test with different company descriptions
    company_descriptions = [
        # Default eon.health description
        "eon.health: A comprehensive Space-Time Health OS platform that leverages advanced AI to transform raw biometric data into actionable insights for personalized health optimization.",
        
        # AI-focused company
        "TechHealth AI: We specialize in cutting-edge artificial intelligence and machine learning solutions for healthcare, developing advanced algorithms that can predict health outcomes with unprecedented accuracy.",
        
        # Device-focused company
        "WearableHealth Systems: We design and manufacture next-generation wearable devices and sensors for continuous health monitoring, focusing on seamless integration with daily life.",
        
        # Longevity-focused company
        "LifeSpan Technologies: Our mission is extending human healthspan through preventive interventions and anti-aging research, focusing on cellular health optimization and age reversal.",
        
        # Data analytics company
        "HealthData Insights: We provide comprehensive health data analytics and temporal pattern recognition services, helping healthcare providers make data-driven decisions through advanced analytics platforms."
    ]
    
    print("=== Testing Company Description Impact on Analysis ===\n")
    print(f"Test Post: {test_post['title'][:60]}...\n")
    
    results = []
    
    for i, description in enumerate(company_descriptions):
        company_name = description.split(':')[0]
        print(f"--- Analysis {i+1}: {company_name} ---")
        
        analysis = analyze_post_for_eon_health(test_post, description)
        results.append((company_name, analysis))
        
        print(f"Relevance Score: {analysis['relevance_score']}%")
        print(f"Detected Themes: {', '.join(analysis['detected_themes'])}")
        print(f"Key Takeaway: {analysis['takeaways'][0] if analysis['takeaways'] else 'None'}")
        print(f"Response Strategy: {analysis['suggested_response'][:100]}...")
        print(f"Targeting Insight: {analysis['targeting_insights'][:100]}...")
        print("-" * 80)
    
    # Compare results
    print("\n=== Comparison Summary ===")
    print("Company Focus -> Relevance Score | Key Differences")
    print("-" * 60)
    
    for company_name, analysis in results:
        focus = "AI" if "AI" in company_name else "Device" if "Wearable" in company_name else "Longevity" if "LifeSpan" in company_name else "Data" if "Data" in company_name else "General"
        print(f"{focus:12} -> {analysis['relevance_score']:5.1f}% | {len(analysis['detected_themes'])} themes detected")
    
    print(f"\nHighest Relevance: {max(results, key=lambda x: x[1]['relevance_score'])[0]} ({max(results, key=lambda x: x[1]['relevance_score'])[1]['relevance_score']}%)")
    print(f"Lowest Relevance:  {min(results, key=lambda x: x[1]['relevance_score'])[0]} ({min(results, key=lambda x: x[1]['relevance_score'])[1]['relevance_score']}%)")
    
    # Show how responses differ
    print("\n=== Response Strategy Differences ===")
    for company_name, analysis in results:
        if "AI" in company_name:
            print(f"{company_name}: Emphasizes AI sophistication")
        elif "Wearable" in company_name:
            print(f"{company_name}: Focuses on device integration")
        elif "LifeSpan" in company_name:
            print(f"{company_name}: Highlights longevity mission")
        elif "Data" in company_name:
            print(f"{company_name}: Leads with analytics capabilities")
        else:
            print(f"{company_name}: General health platform positioning")

if __name__ == "__main__":
    test_company_description_impact()