#!/usr/bin/env python
"""설 연휴 교통상황 블로그 자동 생성 - 2026.02.15"""
import os
import time

os.environ['NO_COLOR'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

log_file = open('seollal_traffic_log.txt', 'w', encoding='utf-8')

def log(msg):
    log_file.write(msg + '\n')
    log_file.flush()

log("=" * 70)
log("트렌드 블로그: 설 연휴 귀성길 뚫는 법! 2월 15일 고속도로 실시간 현황")
log("날짜: 2026-02-15 | 트렌드: 귀성 정체 피크 + 통행료 면제")
log("=" * 70)

try:
    from notebooklm_tools.core.auth import load_cached_tokens
    from notebooklm_tools.core.client import NotebookLMClient
    import httpx

    tokens = load_cached_tokens()
    client = NotebookLMClient(cookies=tokens.cookies)
    
    # 넉넉한 타임아웃 설정
    if hasattr(client, '_client') or hasattr(client, 'client'):
        http_client = getattr(client, '_client', None) or getattr(client, 'client', None)
        if http_client and isinstance(http_client, httpx.Client):
            http_client._transport = httpx.HTTPTransport()
            
    log("[OK] Client initialized")

    # 쿼리: 실시간성 + 정보성 강화
    topic = {
        'name': '2026_설연휴_교통상황_2월15일',
        'query': '''2026년 2월 15일 설 연휴 고속도로 교통상황 실시간 예보
2026 설날 통행료 면제 기간 시간
서울 부산 광주 강릉 예상 소요시간 귀성길 정체 피크 시간대
고속도로 교통정보 앱 로드플러스 1588-2504 활용법
서해안고속도로 경부고속도로 영동고속도로 주요 정체 구간 우회도로
휴게소 맛집 및 편의시설 꿀팁''',
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

    # 2. Deep Research 시작 (재시도 로직 포함)
    log(f"\n[2/5] Starting deep research...")
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

        output_file = "2026_설연휴_교통상황_2월15일_blog.md"
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
print("Done! Check seollal_traffic_log.txt")
