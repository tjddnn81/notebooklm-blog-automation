#!/usr/bin/env python
"""Create AI + Real Estate fusion blog via NotebookLM."""
import os
import time

os.environ['NO_COLOR'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

log_file = open('ai_realestate_log.txt', 'w', encoding='utf-8')

def log(msg):
    log_file.write(msg + '\n')
    log_file.flush()

log("=" * 70)
log("융합 콘텐츠: AI 부동산 분석 - 2026 내 집 마련 타이밍")
log("트렌드 융합: 부동산 정책 변화 + AI 붐")
log("=" * 70)

try:
    from notebooklm_tools.core.auth import load_cached_tokens
    from notebooklm_tools.core.client import NotebookLMClient
    
    tokens = load_cached_tokens()
    client = NotebookLMClient(cookies=tokens.cookies)
    log("[OK] Client initialized")
    
    # 융합 주제 정의
    topic = {
        'name': 'AI_부동산_분석_2026_내집마련_타이밍',
        'query': '''2026년 부동산 정책 변화 다주택자 양도세 중과 아파트 매수 타이밍 
AI 부동산 분석 호갱노노 직방 AI 기능 ChatGPT 부동산 시세 분석 방법 
서울 아파트 가격 전망 전세 vs 매매 비교 
내집마련 전략 2026 부동산 시장 전망 실거주 투자''',
    }
    
    # 1. 노트북 생성
    log("\n[1/5] Creating notebook...")
    try:
        nb = client.create_notebook(topic['name'][:40])
        notebook_id = getattr(nb, 'id', None) or getattr(nb, 'notebook_id', None) or str(nb)
        log(f"  Notebook ID: {notebook_id}")
    except Exception as e:
        log(f"  ERROR: {e}")
        raise
    
    # 2. Deep Research 시작
    log(f"\n[2/5] Starting deep research...")
    log(f"  Query: {topic['query'][:80]}...")
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
        raise
    
    # 3. 완료 대기 (최대 8분)
    log("\n[3/5] Polling research status...")
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
        log("  TIMEOUT - but continuing anyway")
    
    # 4. 소스 임포트
    log("\n[4/5] Importing sources...")
    if sources and task_id:
        try:
            client.import_research_sources(notebook_id, task_id, sources)
            log(f"  Imported {len(sources)} sources")
        except Exception as e:
            log(f"  Warning: {e}")
    
    # 5. 한국어 블로그 생성
    log("\n[5/5] Generating Korean blog...")
    try:
        blog = client.create_report(
            notebook_id=notebook_id,
            report_format="Blog Post",
            language="ko"
        )
        artifact_id = blog.get('artifact_id') if isinstance(blog, dict) else None
        log(f"  Artifact ID: {artifact_id}")
        
        # 다운로드 대기
        output_file = "AI_부동산_분석_2026_내집마련_blog.md"
        log(f"  Waiting for generation (60s)...")
        time.sleep(60)
        
        for attempt in range(15):
            try:
                client.download_report(notebook_id, output_file, artifact_id)
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                log(f"\n{'='*70}")
                log("SUCCESS!")
                log(f"{'='*70}")
                log(f"  File: {output_file}")
                log(f"  Size: {len(content)} characters")
                log(f"  Sources: {len(sources) if sources else 'N/A'}")
                break
            except Exception as e:
                log(f"  Attempt {attempt+1}: {e}")
                time.sleep(20)
        
    except Exception as e:
        log(f"  ERROR: {e}")
        import traceback
        log(traceback.format_exc())

except Exception as e:
    log(f"FATAL ERROR: {e}")
    import traceback
    log(traceback.format_exc())

log_file.close()
print("Done! Check ai_realestate_log.txt")
