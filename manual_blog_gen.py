#!/usr/bin/env python
"""Manual import and blog generation for completed research."""
import os
import time
os.environ['NO_COLOR'] = '1'
import subprocess

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

notebooks = [
    {
        'name': 'Galaxy S26 Ultra',
        'notebook_id': '63c97d9e-c2fa-464b-9092-11f6da39877f',
        'task_id': '725f1f8d-74b5-4984-9ee0-e08f1d4bb16f',
        'status': 'research_completed'
    },
    {
        'name': '2026 Korea Elections',
        'notebook_id': '183d876f-c633-45c2-b443-bb287d8122bd',
        'task_id': 'b5a390be-e36f-4869-930b-87623d57b718',
        'status': 'research_running'
    }
]

print("=" * 70)
print("MANUAL IMPORT & BLOG GENERATION")
print("=" * 70)

tokens = load_cached_tokens()
client = NotebookLMClient(cookies=tokens.cookies)
nlm_path = r"C:\Users\tjddn\AppData\Local\Python\pythoncore-3.14-64\Scripts\nlm.exe"

for nb in notebooks:
    print(f"\n\n[TOPIC] {nb['name']}")
    print(f"  Status: {nb['status']}")
    
    if nb['status'] == 'research_running':
        print("  [SKIP] Research still running, will process later")
        continue
    
    # Import via CLI
    print(f"\n[IMPORT] Via CLI (notebook: {nb['notebook_id']})...")
    try:
        cmd = [nlm_path, "research", "import", nb['notebook_id'], "-y"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300
        )
        
        if result.returncode == 0:
            print("[SUCCESS] Sources imported via CLI")
        else:
            print(f"[WARNING] CLI import issue (might be encoding related)")
            print("  Continuing anyway...")
            
    except Exception as e:
        print(f"[WARNING] Import exception: {e}")
        print("  Continuing anyway...")
    
    # Generate blog
    print(f"\n[BLOG] Creating Korean blog...")
    try:
        blog_result = client.create_report(
            notebook_id=nb['notebook_id'],
            report_format="Blog Post",
            language="ko"
        )
        
        if blog_result and 'artifact_id' in blog_result:
            artifact_id = blog_result['artifact_id']
            print(f"[SUCCESS] Blog created: {artifact_id}")
            
            # Wait for generation
            print("[WAIT] Waiting 60s for blog generation...")
            time.sleep(60)
            
            # Download
            output_file = f"{nb['name'].replace(' ', '_')}_blog.md"
            try:
                client.download_report(nb['notebook_id'], output_file, artifact_id)
                print(f"[SUCCESS] Downloaded: {output_file}")
                
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"\n[INFO] Blog length: {len(content)} chars")
                print(f"[PREVIEW] First line: {content.split(chr(10))[0]}")
                
            except Exception as e:
                print(f"[ERROR] Download failed: {e}")
        else:
            print(f"[ERROR] Blog creation failed: {blog_result}")
            
    except Exception as e:
        print(f"[ERROR] Blog error: {e}")
        import traceback
        traceback.print_exc()

print(f"\n\n{'=' * 70}")
print("[DONE] Check files:")
print("  - Galaxy_S26_Ultra_blog.md")
print("  - 2026_Korea_Local_Elections_blog.md (later)")
print("=" * 70)
