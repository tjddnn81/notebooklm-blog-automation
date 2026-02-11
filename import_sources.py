#!/usr/bin/env python
"""Get sources from completed research and import manually."""
import os
import time
os.environ['NO_COLOR'] = '1'

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens
import inspect

nb_id = '63c97d9e-c2fa-464b-9092-11f6da39877f'
task_id = '725f1f8d-74b5-4984-9ee0-e08f1d4bb16f'

print("=" * 60)
print("MANUAL SOURCE IMPORT FOR GALAXY S26 ULTRA")
print("=" * 60)

tokens = load_cached_tokens()
client = NotebookLMClient(cookies=tokens.cookies)

# Check poll_research to get sources
print(f"\n[POLL] Getting research results...")
poll_result = client.poll_research(nb_id)

print(f"[RESULT] {poll_result}")

if poll_result and isinstance(poll_result, dict):
    sources = poll_result.get('sources') or poll_result.get('results')
    
    if sources:
        print(f"\n[SOURCES] Found {len(sources)} sources!")
        
        # Check import signature
        sig = inspect.signature(client.import_research_sources)
        print(f"\n[API] import_research_sources signature: {sig}")
        
        # Try import
        print(f"\n[IMPORT] Importing {len(sources)} sources...")
        try:
            import_result = client.import_research_sources(nb_id, task_id, sources)
            print(f"[SUCCESS] Import result:{import_result}")
        except Exception as e:
            print(f"[ERROR] Import failed: {e}")
    else:
        print(f"\n[WARNING] No sources found in poll result")
else:
    print(f"\n[ERROR] Poll result invalid")

print("\n" + "=" * 60)
