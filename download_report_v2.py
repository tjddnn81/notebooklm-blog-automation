#!/usr/bin/env python
"""Download report with proper signature inspection."""
import os
import inspect
os.environ['NO_COLOR'] = '1'

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

notebook_id = "5cb04742-19a1-492f-b3b4-d47fc51984cb"
artifact_id = "af55c6c7-7be4-45af-9b99-384d0d615f11"

print("Loading credentials...", flush=True)
tokens = load_cached_tokens()
client = NotebookLMClient(cookies=tokens.cookies)

# Check download_report signature
print("\n1. download_report signature:", flush=True)
sig = inspect.signature(client.download_report)
print(sig, flush=True)

# Get the source code of download_report
print("\n2. download_report source (first 800 chars):", flush=True)
try:
    source = inspect.getsource(client.download_report)
    print(source[:800], flush=True)
except Exception as e:
    print(f"Error: {e}", flush=True)

# Try calling download_report correctly
print("\n3. Calling download_report...", flush=True)
try:
    # Based on signature, try different approaches
    result = client.download_report(notebook_id)
    print(f"Result type: {type(result)}", flush=True)
    
    if isinstance(result, str) and len(result) > 50:
        print("=" * 50)
        print("BLOG CONTENT:")
        print("=" * 50)
        print(result[:3000], flush=True)
        
        with open("milan_olympics_blog.md", "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\n[Saved to milan_olympics_blog.md - {len(result)} chars]", flush=True)
    elif isinstance(result, dict):
        print(f"Dict result: {result}", flush=True)
    else:
        print(f"Result: {result}", flush=True)
except Exception as e:
    print(f"Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
