#!/usr/bin/env python
"""Manual API-based automation to bypass CLI encoding issues."""
import os
import time
os.environ['NO_COLOR'] = '1'

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

# Notebooks already created
notebooks = [
    {
        'id': '63c97d9e-c2fa-464b-9092-11f6da39877f',
        'name': 'Galaxy S26 Ultra Review',
        'query': 'Galaxy S26 Ultra smartphone review features specs camera'
    },
    {
        'id': '183d876f-c633-45c2-b443-bb287d8122bd',
        'name': '2026 Korea Local Elections',
        'query': '2026 Korea local elections candidates policies results'
    }
]

print("=" * 60)
print("MANUAL API AUTOMATION")
print("=" * 60)

tokens = load_cached_tokens()
client = NotebookLMClient(cookies=tokens.cookies)

for nb in notebooks:
    print(f"\n[TOPIC] {nb['name']}")
    print(f"  Notebook ID: {nb['id']}")
    print(f"  Query: {nb['query']}")
    
   # Check API for research methods
    print("\n[API] Checking available methods...")
    research_methods = [m for m in dir(client) if 'research' in m.lower() or 'deep' in m.lower()]
    print(f"  Available: {research_methods}")
    
    # Try start_research if available
    if hasattr(client, 'start_research'):
        print("\n[RESEARCH] Starting via API...")
        try:
            result = client.start_research(
                notebook_id=nb['id'],
                query=nb['query'],
                mode='deep'
            )
            print(f"  Result: {result}")
        except Exception as e:
            print(f"  Error: {e}")
    else:
        print("\n[WARNING] start_research not found in API")
        print("  Deep research must be started via CLI or manually in NotebookLM")

print("\n" + "=" * 60)
print("[DONE] Please check NotebookLM web UI")
print("https://notebooklm.google.com")
print("=" * 60)
