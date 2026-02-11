#!/usr/bin/env python
"""
Automate 2 topics: Galaxy S26 Ultra Review & 2026 Korea Local Elections
Full pipeline: Create Notebook -> Deep Research -> Generate Blog
"""
import os
import subprocess
import time
from datetime import datetime

os.environ['NO_COLOR'] = '1'

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

# Configuration
topics = [
    {
        'name': 'Galaxy S26 Ultra Review',
        'query': 'Galaxy S26 Ultra smartphone review features specs camera',
        'category': 'Tech'
    },
    {
        'name': '2026 Korea Local Elections',
        'query': '2026 Korea local elections candidates policies results',
        'category': 'Politics'
    }
]

nlm_path = r"C:\Users\tjddn\AppData\Local\Python\pythoncore-3.14-64\Scripts\nlm.exe"

def create_notebook(client, title):
    """Create a new notebook."""
    print(f"\n[CREATE] Creating notebook: {title}")
    nb = client.create_notebook(title)
    if nb:
        # Notebook object has .id attribute
        notebook_id = getattr(nb, 'id', None) or getattr(nb, 'notebook_id', None)
        if notebook_id:
            print(f"[SUCCESS] Notebook ID: {notebook_id}")
            return notebook_id
    return None

def start_deep_research(notebook_id, query):
    """Start deep research using CLI."""
    print(f"\n[RESEARCH] Starting deep research...")
    print(f"  Query: {query}")
    
    cmd = [nlm_path, "research", "start", query, "-n", notebook_id, "-m", "deep"]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300
        )
        
        print(f"[RESEARCH] Exit code: {result.returncode}")
        if result.returncode == 0:
            print("[SUCCESS] Deep research started")
            return True
        else:
            print(f"[ERROR] {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def wait_for_research(notebook_id, max_wait=600):
    """Wait for research to complete."""
    print(f"\n[WAIT] Waiting for research to complete (max {max_wait}s)...")
    
    cmd = [nlm_path, "research", "status", notebook_id]
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )
            
            if 'completed' in result.stdout.lower():
                print("[SUCCESS] Research completed!")
                return True
            elif 'failed' in result.stdout.lower():
                print("[ERROR] Research failed")
                return False
            
            print(f"  Still running... ({int(time.time() - start_time)}s elapsed)")
            time.sleep(10)
            
        except Exception as e:
            print(f"[ERROR] Status check failed: {e}")
            time.sleep(10)
    
    print(f"[TIMEOUT] Research exceeded {max_wait}s")
    return False

def import_research(notebook_id):
    """Import research results."""
    print(f"\n[IMPORT] Importing research results...")
    
    cmd = [nlm_path, "research", "import", notebook_id, "-y"]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300
        )
        
        if result.returncode == 0:
            print("[SUCCESS] Research imported")
            return True
        else:
            print(f"[ERROR] Import failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def create_blog(client, notebook_id, title):
    """Create Korean blog post."""
    print(f"\n[BLOG] Creating blog post...")
    
    try:
        result = client.create_report(
            notebook_id=notebook_id,
            report_format="Blog Post",
            language="ko"
        )
        
        if result and 'artifact_id' in result:
            artifact_id = result['artifact_id']
            print(f"[SUCCESS] Blog created: {artifact_id}")
            
            # Wait for completion
            print("[WAIT] Waiting for blog generation...")
            time.sleep(60)
            
            # Download blog
            output_file = f"{title.replace(' ', '_')}_blog.md"
            client.download_report(notebook_id, output_file, artifact_id)
            
            print(f"[SUCCESS] Blog saved: {output_file}")
            return output_file
        else:
            print("[ERROR] Failed to create blog")
            return None
            
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

# Main automation
print("=" * 70)
print("NOTEBOOKLM AUTOMATION: 2 TOPICS")
print("=" * 70)

tokens = load_cached_tokens()
client = NotebookLMClient(cookies=tokens.cookies)

results = []

for i, topic in enumerate(topics, 1):
    print(f"\n\n{'=' * 70}")
    print(f"TOPIC {i}/2: {topic['name']} ({topic['category']})")
    print("=" * 70)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    notebook_title = f"{topic['name'].replace(' ', '_')}_{timestamp}"
    
    # Step 1: Create Notebook
    notebook_id = create_notebook(client, notebook_title)
    if not notebook_id:
        print(f"[FAILED] Topic {i}: Could not create notebook")
        results.append({'topic': topic['name'], 'status': 'FAILED', 'reason': 'Notebook creation failed'})
        continue
    
    # Step 2: Start Deep Research
    if not start_deep_research(notebook_id, topic['query']):
        print(f"[FAILED] Topic {i}: Could not start research")
        results.append({'topic': topic['name'], 'status': 'FAILED', 'reason': 'Research start failed'})
        continue
    
    # Step 3: Wait for Research
    if not wait_for_research(notebook_id, max_wait=600):
        print(f"[FAILED] Topic {i}: Research did not complete")
        results.append({'topic': topic['name'], 'status': 'FAILED', 'reason': 'Research timeout'})
        continue
    
    # Step 4: Import Research
    if not import_research(notebook_id):
        print(f"[FAILED] Topic {i}: Could not import research")
        results.append({'topic': topic['name'], 'status': 'FAILED', 'reason': 'Import failed'})
        continue
    
    # Step 5: Create Blog
    blog_file = create_blog(client, notebook_id, topic['name'])
    if blog_file:
        print(f"[SUCCESS] Topic {i}: Complete!")
        results.append({'topic': topic['name'], 'status': 'SUCCESS', 'notebook_id': notebook_id, 'blog_file': blog_file})
    else:
        print(f"[PARTIAL] Topic {i}: Research done but blog failed")
        results.append({'topic': topic['name'], 'status': 'PARTIAL', 'notebook_id': notebook_id})

# Summary
print(f"\n\n{'=' * 70}")
print("AUTOMATION COMPLETE - SUMMARY")
print("=" * 70)

for i, result in enumerate(results, 1):
    print(f"\nTopic {i}: {result['topic']}")
    print(f"  Status: {result['status']}")
    if 'notebook_id' in result:
        print(f"  Notebook ID: {result['notebook_id']}")
    if 'blog_file' in result:
        print(f"  Blog File: {result['blog_file']}")
    if 'reason' in result:
        print(f"  Reason: {result['reason']}")

print(f"\n{'=' * 70}")
