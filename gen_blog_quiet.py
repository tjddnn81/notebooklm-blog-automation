#!/usr/bin/env python
"""Generate blogs quietly (file logging)."""
import os
import time
os.environ['NO_COLOR'] = '1'

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

notebooks = [
    ('Galaxy S26 Ultra', '63c97d9e-c2fa-464b-9092-11f6da39877f'),
]

with open('blog_log.txt', 'w', encoding='utf-8') as log:
    log.write("BLOG GENERATION\n")
    log.write("=" * 60 + "\n\n")
    
    tokens = load_cached_tokens()
    client = NotebookLMClient(cookies=tokens.cookies)
    
    for name, nb_id in notebooks:
        log.write(f"\n[TOPIC] {name}\n")
        log.write(f"  Notebook: {nb_id}\n")
        
        try:
            blog_result = client.create_report(
                notebook_id=nb_id,
                report_format="Blog Post",
                language="ko"
            )
            
            if blog_result and 'artifact_id' in blog_result:
                artifact_id = blog_result['artifact_id']
                log.write(f"[SUCCESS] Blog created: {artifact_id}\n")
                
                # Wait
                log.write("[WAIT] Waiting 60s...\n")
                time.sleep(60)
                
                # Download
                output_file = f"{name.replace(' ', '_')}_blog.md"
                client.download_report(nb_id, output_file, artifact_id)
                
                # Check size
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                log.write(f"[DOWNLOADED] {output_file} ({len(content)} chars)\n")
                
            else:
                log.write(f"[ERROR] Blog creation failed\n")
                
        except Exception as e:
            log.write(f"[ERROR] {str(e)}\n")
    
    log.write("\n" + "=" * 60 + "\n")

print("Blog generation complete! Check blog_log.txt")
