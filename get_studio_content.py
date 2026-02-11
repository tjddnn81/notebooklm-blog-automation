#!/usr/bin/env python
"""Poll studio and get content from report."""
import os
import time
os.environ['NO_COLOR'] = '1'

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

notebook_id = "5cb04742-19a1-492f-b3b4-d47fc51984cb"

print("Loading credentials...", flush=True)
tokens = load_cached_tokens()
client = NotebookLMClient(cookies=tokens.cookies)

print("Polling studio status...", flush=True)
try:
    # Check poll_studio_status signature
    import inspect
    sig = inspect.signature(client.poll_studio_status)
    print(f"poll_studio_status signature: {sig}", flush=True)
    
    # Try poll_studio_status
    status = client.poll_studio_status(notebook_id)
    print(f"Studio status: {status}", flush=True)
    
    if status:
        # Look for reports
        for item in status if isinstance(status, list) else [status]:
            print(f"Item: {item}", flush=True)
            if isinstance(item, dict):
                content = item.get('content') or item.get('text') or item.get('markdown')
                if content:
                    print("=" * 50, flush=True)
                    print("FOUND CONTENT:", flush=True)
                    print("=" * 50, flush=True)
                    print(content[:3000], flush=True)
                    
                    with open("milan_olympics_blog.md", "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"\nSaved to milan_olympics_blog.md ({len(content)} chars)", flush=True)
                    break
                    
except Exception as e:
    print(f"Error: {e}", flush=True)
    import traceback
    traceback.print_exc()

# Alternative: try get_studio_status
print("\nTrying get_studio_status...", flush=True)
try:
    sig = inspect.signature(client.get_studio_status)
    print(f"get_studio_status signature: {sig}", flush=True)
except Exception as e:
    print(f"Signature error: {e}")
