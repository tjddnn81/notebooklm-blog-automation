#!/usr/bin/env python
"""Get the actual report content from NotebookLM."""
import os
os.environ['NO_COLOR'] = '1'

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

notebook_id = "5cb04742-19a1-492f-b3b4-d47fc51984cb"
artifact_id = "af55c6c7-7be4-45af-9b99-384d0d615f11"

print("Loading credentials...", flush=True)
tokens = load_cached_tokens()
client = NotebookLMClient(cookies=tokens.cookies)

# Method 1: list_notes
print("\n1. Trying list_notes...", flush=True)
try:
    notes = client.list_notes(notebook_id)
    print(f"Notes: {notes}", flush=True)
    if notes:
        for note in notes:
            if isinstance(note, dict):
                content = note.get('content') or note.get('text')
                if content and len(content) > 100:
                    print(f"Found note with content ({len(content)} chars):", flush=True)
                    print(content[:1000], flush=True)
except Exception as e:
    print(f"list_notes Error: {e}", flush=True)

# Method 2: Check get_note
print("\n2. Trying get_note...", flush=True)
try:
    import inspect
    sig = inspect.signature(client.get_note)
    print(f"get_note signature: {sig}", flush=True)
except Exception as e:
    print(f"Signature Error: {e}", flush=True)

# Method 3: Try to get notebook summary which might include generated content
print("\n3. Trying get_notebook_summary...", flush=True)
try:
    summary = client.get_notebook_summary(notebook_id)
    print(f"Summary: {summary}", flush=True)
except Exception as e:
    print(f"Summary error: {e}", flush=True)

# Method 4: Download methods inspection
print("\n4. Available download methods:", flush=True)
download_methods = [m for m in dir(client) if 'download' in m.lower()]
print(download_methods, flush=True)

# Method 5: Try downloading with content API
print("\n5. Trying get_interactive_html (might contain report)...", flush=True)
try:
    methods_with_get = [m for m in dir(client) if 'get' in m.lower() and 'interactive' in m.lower()]
    print(f"Interactive methods: {methods_with_get}", flush=True)
except Exception as e:
    print(f"Error: {e}", flush=True)
