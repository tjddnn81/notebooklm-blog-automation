#!/usr/bin/env python
"""Automate 3 trending topics with file logging to avoid cp949 errors."""
import os
import sys
import time

os.environ['NO_COLOR'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Redirect stdout to log file
log_file = open('trends_log.txt', 'w', encoding='utf-8')

def log(msg):
    log_file.write(msg + '\n')
    log_file.flush()

log("=" * 70)
log("GOOGLE TRENDS 3개 주제 자동화")
log("=" * 70)

try:
    from notebooklm_tools.core.auth import load_cached_tokens
    from notebooklm_tools.core.client import NotebookLMClient
    
    tokens = load_cached_tokens()
    client = NotebookLMClient(cookies=tokens.cookies)
    log("[OK] Client initialized")
    
    # 3개 주제
    topics = [
        {
            'name': 'ICC_T20_World_Cup_2026',
            'query': 'ICC T20 World Cup 2026 경기일정 결과 조편성 시청방법 India vs USA'
        },
        {
            'name': '안세영_배드민턴_아시아단체선수권_우승',
            'query': '안세영 배드민턴 아시아단체선수권 우승 중국전 결승 한국 여자 대표팀'
        },
        {
            'name': '정원오_서울시장_출마',
            'query': '정원오 서울시장 출마 성동구청장 2026 지방선거 공약 더불어민주당'
        }
    ]
    
    results = []
    
    for i, topic in enumerate(topics, 1):
        log(f"\n{'='*60}")
        log(f"[TOPIC {i}/3] {topic['name']}")
        log(f"{'='*60}")
        
        # 1. 노트북 생성
        log("[1/5] Creating notebook...")
        try:
            nb = client.create_notebook(topic['name'][:40])
            notebook_id = getattr(nb, 'id', None) or getattr(nb, 'notebook_id', None) or str(nb)
            log(f"  Notebook ID: {notebook_id}")
        except Exception as e:
            log(f"  ERROR: {e}")
            continue
        
        # 2. Deep Research 시작
        log(f"[2/5] Starting deep research: {topic['query'][:50]}...")
        try:
            research = client.start_research(
                notebook_id=notebook_id,
                query=topic['query'],
                mode='deep'
            )
            task_id = research.get('task_id') if isinstance(research, dict) else None
            log(f"  Task ID: {task_id}")
        except Exception as e:
            log(f"  ERROR: {e}")
            continue
        
        # 3. 완료 대기 (최대 8분)
        log("[3/5] Polling research status...")
        max_wait = 480
        start = time.time()
        completed = False
        sources = None
        
        while time.time() - start < max_wait:
            try:
                poll = client.poll_research(notebook_id)
                if poll and isinstance(poll, dict):
                    state = poll.get('state') or poll.get('status')
                    sources = poll.get('sources') or poll.get('results')
                    
                    if state == 'completed' or state == 'done' or sources:
                        log(f"  COMPLETED! Sources: {len(sources) if sources else 0}")
                        completed = True
                        break
                    elif 'fail' in str(state).lower():
                        log(f"  FAILED: {state}")
                        break
                
                elapsed = int(time.time() - start)
                log(f"  Waiting... ({elapsed}s)")
                time.sleep(25)
                
            except Exception as e:
                log(f"  Warning: {e}")
                time.sleep(25)
        
        if not completed:
            log("  TIMEOUT - skipping")
            continue
        
        # 4. 소스 임포트
        log("[4/5] Importing sources...")
        if sources and task_id:
            try:
                client.import_research_sources(notebook_id, task_id, sources)
                log(f"  Imported {len(sources)} sources")
            except Exception as e:
                log(f"  ERROR: {e}")
        else:
            log("  Skipping import (no sources or task_id)")
        
        # 5. 한국어 블로그 생성
        log("[5/5] Generating Korean blog...")
        try:
            blog = client.create_report(
                notebook_id=notebook_id,
                report_format="Blog Post",
                language="ko"
            )
            artifact_id = blog.get('artifact_id') if isinstance(blog, dict) else None
            log(f"  Artifact ID: {artifact_id}")
            
            # 다운로드 대기
            output_file = f"{topic['name'][:25]}_blog.md"
            log(f"  Waiting for generation...")
            time.sleep(60)  # 1분 대기
            
            for attempt in range(15):
                try:
                    client.download_report(notebook_id, output_file, artifact_id)
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content_len = len(f.read())
                    log(f"  DOWNLOADED: {output_file} ({content_len} chars)")
                    results.append({'name': topic['name'], 'file': output_file, 'chars': content_len})
                    break
                except Exception as e:
                    log(f"  Attempt {attempt+1}: {e}")
                    time.sleep(20)
            
        except Exception as e:
            log(f"  ERROR: {e}")
    
    # 요약
    log(f"\n{'='*70}")
    log("COMPLETE - SUMMARY")
    log(f"{'='*70}")
    for r in results:
        log(f"  [OK] {r['name']}: {r['file']} ({r['chars']} chars)")
    log(f"\nTotal: {len(results)}/3 blogs generated")
    
except Exception as e:
    log(f"FATAL ERROR: {e}")
    import traceback
    log(traceback.format_exc())

log_file.close()
print("Done! Check trends_log.txt")
