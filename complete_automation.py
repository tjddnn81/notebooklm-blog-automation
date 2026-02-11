#!/usr/bin/env python
"""Poll research status, import, and generate blogs."""
import os
import time
os.environ['NO_COLOR'] = '1'

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

tasks = [
    {
        'name': 'Galaxy S26 Ultra',
        'notebook_id': '63c97d9e-c2fa-464b-9092-11f6da39877f',
        'task_id': '725f1f8d-74b5-4984-9ee0-e08f1d4bb16f'
    },
    {
        'name': '2026 Korea Elections',
        'notebook_id': '183d876f-c633-45c2-b443-bb287d8122bd',
        'task_id': 'b5a390be-e36f-4869-930b-87623d57b718'
    }
]

print("=" * 70)
print("RESEARCH MONITOR & BLOG GENERATOR")
print("=" * 70)

tokens = load_cached_tokens()
client = NotebookLMClient(cookies=tokens.cookies)

for task in tasks:
    print(f"\n\n[TOPIC] {task['name']}")
    print(f"  Notebook: {task['notebook_id']}")
    print(f"  Task: {task['task_id']}")
    
    # Poll research status
    print("\n[POLLING] Waiting for research completion (max 10 min)...")
    max_wait = 600  # 10 minutes
    start_time = time.time()
    completed = False
    
    while time.time() - start_time < max_wait:
        try:
            status = client.poll_research(task['notebook_id'])
            
            # Check if completed
            if status and isinstance(status, dict):
                state = status.get('state') or status.get('status')
                if state == 'completed' or state == 'done':
                    print(f"[SUCCESS] Research completed!")
                    completed = True
                    break
                elif 'fail' in str(state).lower():
                    print(f"[ERROR] Research failed: {state}")
                    break
            
            elapsed = int(time.time() - start_time)
            print(f"  Still running... ({elapsed}s elapsed)")
            time.sleep(20)
            
        except Exception as e:
            print(f"[WARNING] Poll error: {e}")
            time.sleep(20)
    
    if not completed:
        print(f"[TIMEOUT] Research exceeded {max_wait}s")
        continue
    
    # Import research sources
    print("\n[IMPORT] Importing sources...")
    try:
        import_result = client.import_research_sources(task['notebook_id'])
        print(f"[SUCCESS] Sources imported!")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        continue
    
    # Generate blog
    print("\n[BLOG] Creating Korean blog post...")
    try:
        blog_result = client.create_report(
            notebook_id=task['notebook_id'],
            report_format="Blog Post",
            language="ko"
        )
        
        if blog_result and 'artifact_id' in blog_result:
            artifact_id = blog_result['artifact_id']
            print(f"[SUCCESS] Blog created: {artifact_id}")
            
            # Wait for blog generation
            print("[WAIT] Waiting for blog generation (60s)...")
            time.sleep(60)
            
            # Download blog
            output_file = f"{task['name'].replace(' ', '_')}_blog.md"
            try:
                client.download_report(task['notebook_id'], output_file, artifact_id)
                print(f"[SUCCESS] Blog downloaded: {output_file}")
                
                # Show preview
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"\n[PREVIEW] First 500 chars:")
                print(content[:500])
                print(f"\n[INFO] Total: {len(content)} chars")
                
            except Exception as e:
                print(f"[ERROR] Download failed: {e}")
        else:
            print(f"[ERROR] Blog creation failed")
            
    except Exception as e:
        print(f"[ERROR] Blog generation error: {e}")

print(f"\n\n{'=' * 70}")
print("AUTOMATION COMPLETE!")
print("=" * 70)
