#!/usr/bin/env python
"""Process Korea Elections topic - import and blog generation."""
import os
import time
os.environ['NO_COLOR'] = '1'

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

nb_id = '183d876f-c633-45c2-b443-bb287d8122bd'
task_id = 'b5a390be-e36f-4869-930b-87623d57b718'

with open('elections_log.txt', 'w', encoding='utf-8') as log:
    log.write("2026 KOREA LOCAL ELECTIONS - PROCESSING\n")
    log.write("=" * 60 + "\n\n")
    
    tokens = load_cached_tokens()
    client = NotebookLMClient(cookies=tokens.cookies)
    
    # Poll research
    log.write("[POLL] Getting research results...\n")
    poll_result = client.poll_research(nb_id)
    
    if poll_result and isinstance(poll_result, dict):
        sources = poll_result.get('sources') or poll_result.get('results')
        
        if sources:
            log.write(f"[SOURCES] Found {len(sources)} sources\n")
            
            # Import
            log.write(f"[IMPORT] Importing...\n")
            try:
                client.import_research_sources(nb_id, task_id, sources)
                log.write(f"[SUCCESS] Imported!\n")
            except Exception as e:
                log.write(f"[ERROR] {str(e)}\n")
            
            # Generate blog
            log.write(f"\n[BLOG] Creating Korean blog...\n")
            try:
                blog_result = client.create_report(
                    notebook_id=nb_id,
                    report_format="Blog Post",
                    language="ko"
                )
                
                if blog_result and 'artifact_id' in blog_result:
                    artifact_id = blog_result['artifact_id']
                    log.write(f"[SUCCESS] Blog created: {artifact_id}\n")
                    
                    # Poll download
                    log.write("[DOWNLOAD] Polling for completion...\n")
                    output_file = '2026_Korea_Local_Elections_blog.md'
                    
                    for i in range(24):
                        log.write(f"  Attempt {i+1}/24\n")
                        time.sleep(20)
                        
                        try:
                            client.download_report(nb_id, output_file, artifact_id)
                            
                            with open(output_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            log.write(f"[DOWNLOADED] {len(content)} chars\n")
                            log.write(f"  First line: {content.split(chr(10))[0]}\n")
                            break
                        except Exception as e:
                            if 'not ready' in str(e):
                                continue
                            else:
                                log.write(f"[ERROR] {str(e)}\n")
                                break
                else:
                    log.write(f"[ERROR] Blog creation failed\n")
                    
            except Exception as e:
                log.write(f"[ERROR] {str(e)}\n")
        else:
            log.write("[WARNING] No sources found\n")
    else:
        log.write("[ERROR] Poll result invalid\n")
    
    log.write("\n" + "=" * 60 + "\n")

print("Elections processing complete! Check elections_log.txt")
