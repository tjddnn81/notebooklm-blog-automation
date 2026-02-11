#!/usr/bin/env python
"""Import sources WITHOUT printing to console (to avoid cp949)."""
import os
import time
os.environ['NO_COLOR'] = '1'

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

nb_id = '63c97d9e-c2fa-464b-9092-11f6da39877f'
task_id = '725f1f8d-74b5-4984-9ee0-e08f1d4bb16f'

with open('import_log.txt', 'w', encoding='utf-8') as log:
    log.write("GALAXY S26 ULTRA - SOURCE IMPORT\n")
    log.write("=" * 60 + "\n\n")
    
    tokens = load_cached_tokens()
    client = NotebookLMClient(cookies=tokens.cookies)
    
    # Poll research
    log.write("[POLL] Getting research results...\n")
    poll_result = client.poll_research(nb_id)
    log.write(f"[RESULT TYPE] {type(poll_result)}\n")
    
    if poll_result and isinstance(poll_result, dict):
        sources = poll_result.get('sources') or poll_result.get('results')
        
        if sources:
            log.write(f"[SOURCES] Found {len(sources)} sources\n")
            
            # Import
            log.write(f"[IMPORT] Importing...\n")
            try:
                import_result = client.import_research_sources(nb_id, task_id, sources)
                log.write(f"[SUCCESS] Imported!\n")
            except Exception as e:
                log.write(f"[ERROR] {str(e)}\n")
        else:
            log.write("[WARNING] No sources found\n")
    else:
        log.write("[ERROR] Poll result invalid\n")
    
    log.write("\n" + "=" * 60 + "\n")

# Print only safe message
print("Check import_log.txt for results")
