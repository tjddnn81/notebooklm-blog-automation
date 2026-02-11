#!/usr/bin/env python
"""Verify NotebookLM content via API - No emojis for Windows."""
import os
os.environ['NO_COLOR'] = '1'

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

notebook_id = "5cb04742-19a1-492f-b3b4-d47fc51984cb"

print("=" * 60)
print("[CHECK] NotebookLM Content Verification")
print("=" * 60)

tokens = load_cached_tokens()
client = NotebookLMClient(cookies=tokens.cookies)

# 1. Notebook info
print("\n[NOTEBOOK INFO]")
print(f"   ID: {notebook_id}")

# 2. Notebook summary
print("\n[NOTEBOOK SUMMARY]")
summary = client.get_notebook_summary(notebook_id)
if summary and 'summary' in summary:
    for line in summary['summary']:
        print(f"   {line[:200]}...")

# 3. Studio status (generated reports)
print("\n[STUDIO ARTIFACTS]")
status = client.poll_studio_status(notebook_id)
for item in status:
    print(f"   - Title: {item.get('title', 'N/A')}")
    print(f"     Type: {item.get('type', 'N/A')}")
    print(f"     Status: {item.get('status', 'N/A')}")
    print(f"     Created: {item.get('created_at', 'N/A')}")
    print(f"     Artifact ID: {item.get('artifact_id', 'N/A')}")

# 4. Local file check
print("\n[LOCAL FILE]")
blog_path = "milan_olympics_blog.md"
if os.path.exists(blog_path):
    with open(blog_path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"   File: {blog_path}")
    print(f"   Size: {len(content)} chars")
    first_line = content.split('\n')[0] if content else 'N/A'
    print(f"   First line: {first_line}")
else:
    print("   File not found!")

print("\n" + "=" * 60)
print("[SUCCESS] Verification Complete!")
print("=" * 60)
