#!/usr/bin/env python
"""Fetch Google Trends for 2026-02-08 and select 2 topics."""
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

print("=" * 60)
print("Google Trends Fetcher - 2026-02-08")
print("=" * 60)

# Try to fetch real-time trending searches
trending_url = "https://trends.google.com/trending/rss?geo=KR"

print(f"\n[FETCHING] {trending_url}")

try:
    with urllib.request.urlopen(trending_url, timeout=10) as response:
        xml_data = response.read()
    
    print("[SUCCESS] RSS data retrieved")
    
    # Parse XML
    root = ET.fromstring(xml_data)
    
    trends = []
    for item in root.findall('.//item'):
        title_elem = item.find('title')
        traffic_elem = item.find('.//ht:approx_traffic', {'ht': 'http://www.google.com/trends/hottrends'})
        
        if title_elem is not None:
            title = title_elem.text
            traffic = traffic_elem.text if traffic_elem is not None else 'N/A'
            trends.append({'title': title, 'traffic': traffic})
    
    print(f"\n[FOUND] {len(trends)} trending topics:")
    for i, trend in enumerate(trends[:10], 1):
        print(f"  {i}. {trend['title']} ({trend['traffic']})")
    
    # Select top 2 non-Olympic topics
    selected = []
    for trend in trends:
        if len(selected) >= 2:
            break
        # Skip if similar to Milan Olympics (already done)
        if 'olympic' not in trend['title'].lower() and 'milan' not in trend['title'].lower():
            selected.append(trend['title'])
    
    print(f"\n[SELECTED] 2 topics for automation:")
    for i, topic in enumerate(selected, 1):
        print(f"  {i}. {topic}")
    
    # Save to file
    with open('selected_trends.txt', 'w', encoding='utf-8') as f:
        for topic in selected:
            f.write(f"{topic}\n")
    
    print(f"\n[SAVED] selected_trends.txt")

except Exception as e:
    print(f"\n[ERROR] Failed to fetch trends: {e}")
    print("\n[FALLBACK] Using pre-defined topics from task.md:")
    
    # Fallback to remaining topics from task.md
    fallback_topics = [
        "Galaxy S26 Ultra Review",
        "2026 Korea Local Elections"
    ]
    
    for i, topic in enumerate(fallback_topics, 1):
        print(f"  {i}. {topic}")
    
    with open('selected_trends.txt', 'w', encoding='utf-8') as f:
        for topic in fallback_topics:
            f.write(f"{topic}\n")
    
    print(f"\n[SAVED] selected_trends.txt (fallback)")

print("\n" + "=" * 60)
