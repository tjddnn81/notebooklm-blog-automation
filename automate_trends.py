#!/usr/bin/env python
"""Automate 3 trending topics from Google Trends Korea."""
import os
import time
os.environ['NO_COLOR'] = '1'

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

# 선정된 3개 주제
topics = [
    {
        'name': 'ICC T20 World Cup 2026',
        'query': 'ICC T20 World Cup 2026 경기일정 결과 조편성 시청방법',
        'category': 'Sports'
    },
    {
        'name': '안세영 배드민턴 아시아단체선수권 우승',
        'query': '안세영 배드민턴 아시아단체선수권 우승 중국전 결승 성적',
        'category': 'Sports'
    },
    {
        'name': '정원오 서울시장 출마',
        'query': '정원오 서울시장 출마 성동구청장 2026 지방선거 공약',
        'category': 'Politics'
    }
]

with open('trends_automation_log.txt', 'w', encoding='utf-8') as log:
    log.write("=" * 70 + "\n")
    log.write("GOOGLE TRENDS 기반 3개 주제 자동화\n")
    log.write(f"실행시각: 2026-02-08 18:30\n")
    log.write("=" * 70 + "\n\n")
    
    tokens = load_cached_tokens()
    client = NotebookLMClient(cookies=tokens.cookies)
    
    results = []
    
    for i, topic in enumerate(topics, 1):
        log.write(f"\n{'='*60}\n")
        log.write(f"[TOPIC {i}/3] {topic['name']} ({topic['category']})\n")
        log.write(f"{'='*60}\n")
        
        # 1. Create notebook
        log.write(f"\n[1/5] Creating notebook...\n")
        try:
            nb = client.create_notebook(topic['name'].replace(' ', '_')[:40])
            notebook_id = getattr(nb, 'id', None) or getattr(nb, 'notebook_id', None)
            log.write(f"  [SUCCESS] Notebook ID: {notebook_id}\n")
        except Exception as e:
            log.write(f"  [ERROR] {str(e)}\n")
            continue
        
        # 2. Start deep research
        log.write(f"\n[2/5] Starting deep research...\n")
        log.write(f"  Query: {topic['query']}\n")
        try:
            research = client.start_research(
                notebook_id=notebook_id,
                query=topic['query'],
                mode='deep'
            )
            task_id = research.get('task_id')
            log.write(f"  [SUCCESS] Task ID: {task_id}\n")
        except Exception as e:
            log.write(f"  [ERROR] {str(e)}\n")
            continue
        
        # 3. Poll for completion (max 10 min)
        log.write(f"\n[3/5] Polling research status...\n")
        max_wait = 600
        start = time.time()
        completed = False
        sources = None
        
        while time.time() - start < max_wait:
            try:
                poll = client.poll_research(notebook_id)
                if poll and isinstance(poll, dict):
                    state = poll.get('state') or poll.get('status')
                    sources = poll.get('sources') or poll.get('results')
                    
                    if state == 'completed' or state == 'done':
                        log.write(f"  [SUCCESS] Research completed!\n")
                        completed = True
                        break
                    elif 'fail' in str(state).lower():
                        log.write(f"  [ERROR] Research failed\n")
                        break
                        
                elapsed = int(time.time() - start)
                log.write(f"  Still running... ({elapsed}s)\n")
                time.sleep(30)
                
            except Exception as e:
                log.write(f"  [WARNING] {str(e)}\n")
                time.sleep(30)
        
        if not completed:
            log.write(f"  [TIMEOUT] Skipping...\n")
            continue
        
        # 4. Import sources
        log.write(f"\n[4/5] Importing sources...\n")
        if sources:
            log.write(f"  Found {len(sources)} sources\n")
            try:
                client.import_research_sources(notebook_id, task_id, sources)
                log.write(f"  [SUCCESS] Sources imported\n")
            except Exception as e:
                log.write(f"  [ERROR] {str(e)}\n")
        
        # 5. Generate Korean blog
        log.write(f"\n[5/5] Generating Korean blog...\n")
        try:
            blog = client.create_report(
                notebook_id=notebook_id,
                report_format="Blog Post",
                language="ko"
            )
            artifact_id = blog.get('artifact_id')
            log.write(f"  [SUCCESS] Artifact: {artifact_id}\n")
            
            # Poll for download
            log.write(f"  Waiting for generation...\n")
            output_file = f"{topic['name'].replace(' ', '_')[:30]}_blog.md"
            
            for attempt in range(20):
                time.sleep(20)
                try:
                    client.download_report(notebook_id, output_file, artifact_id)
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    log.write(f"  [DOWNLOADED] {output_file} ({len(content)} chars)\n")
                    results.append({
                        'topic': topic['name'],
                        'file': output_file,
                        'chars': len(content)
                    })
                    break
                except Exception as e:
                    if 'not ready' in str(e):
                        continue
                    else:
                        log.write(f"  [ERROR] {str(e)}\n")
                        break
                        
        except Exception as e:
            log.write(f"  [ERROR] {str(e)}\n")
    
    # Summary
    log.write(f"\n\n{'='*70}\n")
    log.write("AUTOMATION COMPLETE - SUMMARY\n")
    log.write(f"{'='*70}\n\n")
    
    for r in results:
        log.write(f"  ✅ {r['topic']}: {r['file']} ({r['chars']} chars)\n")
    
    log.write(f"\nTotal: {len(results)}/3 blogs generated\n")

print("Automation complete! Check trends_automation_log.txt")
