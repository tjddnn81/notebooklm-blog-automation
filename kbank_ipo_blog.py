#!/usr/bin/env python
"""K-Bank IPO Blog Generation Script - 2026.02.15"""
import os
import time

os.environ['NO_COLOR'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

log_file = open('kbank_ipo_log.txt', 'w', encoding='utf-8')

def log(msg):
    log_file.write(msg + '\n')
    log_file.flush()
    print(msg)

log("=" * 70)
log("트렌드 블로그: 케이뱅크(K-Bank) 상장 & 공모주 대박 분석")
log("날짜: 2026-02-15 | 주제: IPO 일정, 예상 공모가, 장외가, 투자 전략")
log("=" * 70)

try:
    from notebooklm_tools.core.auth import load_cached_tokens
    from notebooklm_tools.core.client import NotebookLMClient
    import httpx

    tokens = load_cached_tokens()
    client = NotebookLMClient(cookies=tokens.cookies)
    
    # Increase timeout for deep research with many sources
    if hasattr(client, '_client') or hasattr(client, 'client'):
        http_client = getattr(client, '_client', None) or getattr(client, 'client', None)
        if http_client and isinstance(http_client, httpx.Client):
            http_client._transport = httpx.HTTPTransport()
            
    log("[OK] Client initialized")

    # Comprehensive query for high-quality content
    topic = {
        'name': '2026_K-Bank_IPO_Master_Guide',
        'query': '''2026년 케이뱅크 상장 일정 및 공모주 청약 방법 상세 가이드
케이뱅크 예상 공모가 및 기업 가치(Valuation) 분석
현재 케이뱅크 장외 주식 시세 및 주가 추이 (서울거래 비상장, 38커뮤니케이션 등)
케이뱅크 vs 카카오뱅크 vs 토스뱅크 실적 및 경쟁력 비교 2025년 결산
케이뱅크 IPO 흥행 가능성 및 따상 전망 리스크 요인
공모주 청약 증권사 및 우대 조건 계좌 개설 꿀팁
2026년 국내 IPO 시장 전망 및 대어급 종목 리스트''',
    }

    # 1. Create Notebook
    log("\n[1/5] Creating notebook...")
    try:
        nb = client.create_notebook(topic['name'][:40])
        notebook_id = getattr(nb, 'id', None) or getattr(nb, 'notebook_id', None) or str(nb)
        log(f"  Notebook ID: {notebook_id}")
    except Exception as e:
        log(f"  ERROR: {e}")
        raise

    # 2. Start Deep Research (with aggressive retries)
    log(f"\n[2/5] Starting deep research (Maximizing sources)...")
    log(f"  Query: {topic['query'][:80]}...")
    
    research = None
    for retry in range(3):
        try:
            research = client.start_research(
                notebook_id=notebook_id,
                query=topic['query'],
                mode='deep'
            )
            task_id = research.get('task_id') if isinstance(research, dict) else None
            log(f"  Task ID: {task_id}")
            break
        except Exception as e:
            log(f"  Retry {retry+1}/3: {e}")
            time.sleep(10)
    
    if not research:
        raise Exception("start_research failed after 3 retries")

    # 3. Poll for Completion (Wait longer for more sources)
    log("\n[3/5] Polling research status...")
    max_wait = 600  # 10 minutes max for high quality
    start = time.time()
    completed = False
    sources = None

    while time.time() - start < max_wait:
        try:
            poll = client.poll_research(notebook_id)
            if poll and isinstance(poll, dict):
                state = poll.get('state') or poll.get('status')
                sources = poll.get('sources') or poll.get('results') or []

                # Wait until at least 20 sources if possible, or 'completed' state
                if (state == 'completed' or state == 'done') and len(sources) > 0:
                    log(f"  COMPLETED! Sources found: {len(sources)}")
                    completed = True
                    break
                elif 'fail' in str(state).lower():
                    log(f"  FAILED: {state}")
                    break
                
                # Log progress
                if sources:
                   print(f"  Collecting sources... Current count: {len(sources)}", end='\r')

            elapsed = int(time.time() - start)
            if elapsed % 30 == 0:
                log(f"  Waiting... ({elapsed}s)")
            time.sleep(10)

        except Exception as e:
            log(f"  Warning polling: {e}")
            time.sleep(20)

    if not completed:
        log("  TIMEOUT - attempting to proceed with whatever sources we have")

    # 4. Import Sources
    log("\n[4/5] Importing sources...")
    if sources and task_id:
        try:
            client.import_research_sources(notebook_id, task_id, sources)
            log(f"  Imported {len(sources)} sources")
        except Exception as e:
            log(f"  Warning importing: {e}")

    # 5. Generate Blog
    log("\n[5/5] Generating premium Korean blog...")
    try:
        blog = client.create_report(
            notebook_id=notebook_id,
            report_format="Blog Post",
            language="ko"
        )
        artifact_id = blog.get('artifact_id') if isinstance(blog, dict) else None
        log(f"  Artifact ID: {artifact_id}")

        output_file = "2026_K뱅크_IPO_공모주_분석_blog.md"
        log(f"  Waiting for generation (60s)...")
        time.sleep(60)

        for attempt in range(15):
            try:
                client.download_report(notebook_id, output_file, artifact_id)
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if len(content) < 100:
                    raise Exception("Content too short, maybe not ready")

                log(f"\n{'='*70}")
                log("SUCCESS! Premium Blog Generated")
                log(f"{'='*70}")
                log(f"  File: {output_file}")
                log(f"  Size: {len(content)} characters")
                log(f"  Sources Used: {len(sources) if sources else 'N/A'}")
                break
            except Exception as e:
                log(f"  Attempt {attempt+1}: {e}")
                time.sleep(20)

    except Exception as e:
        log(f"  ERROR during content generation: {e}")
        import traceback
        log(traceback.format_exc())

except Exception as e:
    log(f"FATAL ERROR: {e}")
    import traceback
    log(traceback.format_exc())

log_file.close()
log("Done! Check kbank_ipo_log.txt")
