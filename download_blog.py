#!/usr/bin/env python
"""Download blog with longer wait time."""
import os
import time
os.environ['NO_COLOR'] = '1'

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

nb_id = '63c97d9e-c2fa-464b-9092-11f6da39877f'
artifact_id = 'eb64a34b-c902-4c3a-920c-db4ae5ecc0ca'
output_file = 'Galaxy_S26_Ultra_blog.md'

with open('download_log.txt', 'w', encoding='utf-8') as log:
    log.write("GALAXY S26 ULTRA - BLOG DOWNLOAD\n")
    log.write("=" * 60 + "\n\n")
    
    tokens = load_cached_tokens()
    client = NotebookLMClient(cookies=tokens.cookies)
    
    # Poll every 20s
    max_attempts = 24  # 8 minutes total
    for i in range(max_attempts):
        log.write(f"[ATTEMPT {i+1}/{max_attempts}] Checking blog status...\n")
        
        try:
            client.download_report(nb_id, output_file, artifact_id)
            log.write(f"[SUCCESS] Downloaded to {output_file}\n")
            
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            log.write(f"[INFO] Blog length: {len(content)} chars\n")
            log.write(f"[INFO] First line: {content.split(chr(10))[0]}\n")
            break
            
        except Exception as e:
            error_msg = str(e)
            if 'not ready' in error_msg:
                log.write(f"  Still generating... Waiting 20s\n")
                time.sleep(20)
            else:
                log.write(f"[ERROR] {error_msg}\n")
                break
    
    log.write("\n" + "=" * 60 + "\n")

print("Download complete! Check download_log.txt and Galaxy_S26_Ultra_blog.md")
