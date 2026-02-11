#!/usr/bin/env python
"""Generate blog report from Milan Olympics notebook - bypass CLI encoding bug."""
import sys
import os

# Suppress Rich console output that causes encoding issues on Windows
os.environ['TERM'] = 'dumb'
os.environ['NO_COLOR'] = '1'

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

notebook_id = "5cb04742-19a1-492f-b3b4-d47fc51984cb"

print("Loading credentials...", flush=True)
tokens = load_cached_tokens()
client = NotebookLMClient(cookies=tokens.cookies)

print(f"Creating Blog Post Report for notebook: {notebook_id}", flush=True)
print(f"Using format: {NotebookLMClient.REPORT_FORMAT_BLOG_POST}", flush=True)

try:
    # Use create_report with correct parameter names
    # Signature: create_report(notebook_id, source_ids=None, report_format="Briefing Doc", custom_prompt="", language="en")
    result = client.create_report(
        notebook_id=notebook_id,
        report_format="Blog Post",  # Not "format"!
        language="ko"  # Korean
    )
    print("=" * 50, flush=True)
    print("REPORT CREATION STARTED!", flush=True)
    print("=" * 50, flush=True)
    print(f"Result: {result}", flush=True)
    
    # Try to get artifact ID and poll/download
    if result:
        artifact_id = result.get('artifact_id') if isinstance(result, dict) else getattr(result, 'artifact_id', None)
        if artifact_id:
            print(f"Artifact ID: {artifact_id}", flush=True)
            print("Polling for completion...", flush=True)
            import time
            for i in range(30):
                time.sleep(10)
                status = client.get_studio_status(notebook_id, artifact_id)
                print(f"Status check {i+1}: {status}", flush=True)
                if status and (status.get('done') or status.get('completed')):
                    print("Report completed! Downloading...", flush=True)
                    content = client.download_report(notebook_id, artifact_id)
                    print("=" * 50, flush=True)
                    print("BLOG CONTENT:", flush=True)
                    print("=" * 50, flush=True)
                    print(content, flush=True)
                    break
except Exception as e:
    print(f"Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
