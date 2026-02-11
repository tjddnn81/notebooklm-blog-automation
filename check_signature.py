#!/usr/bin/env python
"""Check create_report function signature."""
import inspect
from notebooklm_tools.core.client import NotebookLMClient

# Get function signature
print("create_report signature:")
sig = inspect.signature(NotebookLMClient.create_report)
print(sig)

# Get source if possible
try:
    source = inspect.getsource(NotebookLMClient.create_report)
    print("\nFunction source (first 500 chars):")
    print(source[:500])
except:
    pass
