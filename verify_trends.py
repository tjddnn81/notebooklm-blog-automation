#!/usr/bin/env python
"""Process selected trends with better encoding."""
import os

print("Reading selected_trends.txt...")
with open('selected_trends.txt', 'r', encoding='utf-8') as f:
    trends = [line.strip() for line in f if line.strip()]

print(f"\nSelected Trends ({len(trends)}):")
for i, trend in enumerate(trends, 1):
    print(f"  {i}. {trend}")

# If trends look like encoding issues or too vague, use fallback
if len(trends) < 2 or any(len(t) < 3 for t in trends):
    print("\n[FALLBACK] Using predefined topics from task.md")
    trends = [
        "Galaxy S26 Ultra Review",
        "2026 Korea Local Elections"
    ]
    print(f"\nFallback Topics:")
    for i, trend in enumerate(trends, 1):
        print(f"  {i}. {trend}")

# Save clean topics
with open('final_topics.txt', 'w', encoding='utf-8') as f:
    for topic in trends[:2]:
        f.write(f"{topic}\n")

print(f"\n[SAVED] final_topics.txt with {len(trends[:2])} topics")
