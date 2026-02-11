#!/usr/bin/env python
"""Create 스몰웨딩 재테크 fusion blog via NotebookLM."""
import os
import time

os.environ['NO_COLOR'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

log_file = open('smallwedding_invest_log.txt', 'w', encoding='utf-8')

def log(msg):
    log_file.write(msg + '\n')
    log_file.flush()

log("=" * 70)
log("융합 콘텐츠: 스몰웨딩 재테크 - 결혼 비용 아끼고 투자하기")
log("트렌드 융합: 결혼식 필요성 논쟁 + 반도체 주식 급등")
log("=" * 70)

try:
    from notebooklm_tools.core.auth import load_cached_tokens
    from notebooklm_tools.core.client import NotebookLMClient
    
    tokens = load_cached_tokens()
    client = NotebookLMClient(cookies=tokens.cookies)
    log("[OK] Client initialized")
    
    # 융합 주제: 스몰웨딩 + 재테크
    topic = {
        'name': '스몰웨딩_재테크_결혼비용_투자전략',
        'query': '''2026년 스몰웨딩 트렌드 결혼비용 절약 방법 평균 결혼비용 비교
MZ세대 결혼관 변화 결혼식 굳이 안해도 된다 vs 꼭 해야한다
결혼 비용 절약 금액 투자 전략 삼성전자 주식 투자 시뮬레이션
반도체 주식 ETF 추천 신혼부부 재테크 전략 자산 형성
결혼자금 활용법 전세자금 vs 주식투자 신혼집 마련 현실적 전략
웨딩 비용 항목별 절약 팁 스드메 절약 2026''',
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
        log("  TIMEOUT - continuing anyway")
    
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
        
        output_file = "스몰웨딩_재테크_결혼비용_투자전략_blog.md"
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
print("Done! Check smallwedding_invest_log.txt")
