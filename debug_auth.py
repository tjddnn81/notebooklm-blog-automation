#!/usr/bin/env python
"""Debug script to test NotebookLM API connection."""
import os
os.environ['NO_COLOR'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("Starting debug script...")

try:
    from notebooklm_tools.core.auth import load_cached_tokens
    print("Auth module loaded")
    
    tokens = load_cached_tokens()
    print(f"Tokens loaded: {bool(tokens)}")
    print(f"Cookies: {bool(tokens.cookies) if tokens else 'N/A'}")
    
    from notebooklm_tools.core.client import NotebookLMClient
    print("Client module loaded")
    
    client = NotebookLMClient(cookies=tokens.cookies)
    print("Client initialized")
    
    # Test: list notebooks
    notebooks = client.list_notebooks()
    print(f"Found {len(notebooks)} existing notebooks")
    for nb in notebooks[:3]:
        print(f"  - {nb}")
        
    print("\nAPI connection verified!")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
