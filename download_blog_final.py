#!/usr/bin/env python
"""Download report with correct signature: output_path is required."""
import os
os.environ['NO_COLOR'] = '1'

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

notebook_id = "5cb04742-19a1-492f-b3b4-d47fc51984cb"
artifact_id = "af55c6c7-7be4-45af-9b99-384d0d615f11"
output_path = "milan_olympics_blog.md"

print("Loading credentials...", flush=True)
tokens = load_cached_tokens()
client = NotebookLMClient(cookies=tokens.cookies)

print(f"Downloading report to: {output_path}", flush=True)
try:
    # Correct signature: download_report(notebook_id, output_path, artifact_id=None)
    result = client.download_report(notebook_id, output_path, artifact_id)
    print(f"Result: {result}", flush=True)
    
    # Read and display the saved file
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        print("=" * 60)
        print("BLOG POST DOWNLOADED SUCCESSFULLY!")
        print(f"File: {output_path} ({len(content)} chars)")
        print("=" * 60)
        print("\n" + content[:4000])
        if len(content) > 4000:
            print(f"\n... [truncated, {len(content) - 4000} more chars]")
except Exception as e:
    print(f"Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
