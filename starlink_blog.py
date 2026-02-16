#!/usr/bin/env python
"""Tesla Starlink Blog - 참신한 각도의 블로그 생성 (2026.02.16)"""
import os
import time

os.environ['NO_COLOR'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

log_file = open('starlink_blog_log.txt', 'w', encoding='utf-8')

def log(msg):
    log_file.write(msg + '\n')
    log_file.flush()
    print(msg)

log("=" * 70)
log("트렌드 블로그: 테슬라 스타링크 - 다른 블로그와 차별화된 참신한 분석")
log("날짜: 2026-02-16")
log("=" * 70)

try:
    from notebooklm_tools.core.auth import load_cached_tokens
    from notebooklm_tools.core.client import NotebookLMClient
    import httpx

    tokens = load_cached_tokens()
    client = NotebookLMClient(cookies=tokens.cookies)

    if hasattr(client, '_client') or hasattr(client, 'client'):
        http_client = getattr(client, '_client', None) or getattr(client, 'client', None)
        if http_client and isinstance(http_client, httpx.Client):
            http_client._transport = httpx.HTTPTransport()

    log("[OK] Client initialized")

    # 참신한 각도: 단순 "스타링크란?" 이 아닌 심층 분석 쿼리
    topic = {
        'name': 'Tesla_Starlink_2026_Deep_Analysis',
        'query': '''2026년 스타링크(Starlink) 최신 현황 및 위성 수 업데이트 (V2 Mini 포함)
스타링크 다이렉트 투 셀(Direct-to-Cell) 기술 T-Mobile 제휴 현황 2026
일론 머스크 스타링크 한국 상륙 가능성 및 KT SKT LGU+ 통신사 위협 분석
스타링크 vs OneWeb vs 아마존 카이퍼(Kuiper) 우주 인터넷 경쟁 구도
스페이스X 스타쉽(Starship) 발사와 스타링크 V3 대량 배치 계획
스타링크 군사적 활용 우크라이나 전쟁 사례 및 국방 위성통신 전략
스타링크 주가 IPO 상장 전망 2026 투자 가치 분석
스타링크 레이저 인터링크(Laser Interlink) 기술과 광섬유 대체 가능성
자율주행차 테슬라 FSD와 스타링크 연동 V2X 통신 미래
우주 쓰레기(Space Debris) 및 천문학 광공해 논란과 스타링크의 대응''',
    }

    # 1. Notebook 생성
    log("\n[1/5] Creating notebook...")
    try:
        nb = client.create_notebook(topic['name'][:40])
        notebook_id = getattr(nb, 'id', None) or getattr(nb, 'notebook_id', None) or str(nb)
        log(f"  Notebook ID: {notebook_id}")
    except Exception as e:
        log(f"  ERROR: {e}")
        raise

    # 2. Deep Research 시작 (소스 최대화)
    log(f"\n[2/5] Starting deep research (Maximum sources)...")
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

    # 3. 완료 대기
    log("\n[3/5] Polling research status...")
    max_wait = 600
    start = time.time()
    completed = False
    sources = None

    while time.time() - start < max_wait:
        try:
            poll = client.poll_research(notebook_id)
            if poll and isinstance(poll, dict):
                state = poll.get('state') or poll.get('status')
                sources = poll.get('sources') or poll.get('results') or []

                if (state == 'completed' or state == 'done') and len(sources) > 0:
                    log(f"  COMPLETED! Sources found: {len(sources)}")
                    completed = True
                    break
                elif 'fail' in str(state).lower():
                    log(f"  FAILED: {state}")
                    break

            elapsed = int(time.time() - start)
            if elapsed % 30 == 0:
                log(f"  Waiting... ({elapsed}s)")
            time.sleep(10)

        except Exception as e:
            log(f"  Warning polling: {e}")
            time.sleep(20)

    if not completed:
        log("  TIMEOUT - proceeding with available sources")

    # 4. 소스 임포트
    log("\n[4/5] Importing sources...")
    if sources and task_id:
        try:
            client.import_research_sources(notebook_id, task_id, sources)
            log(f"  Imported {len(sources)} sources")
        except Exception as e:
            log(f"  Warning importing: {e}")

    # 5. 블로그 생성
    log("\n[5/5] Generating innovative Starlink blog...")
    try:
        blog = client.create_report(
            notebook_id=notebook_id,
            report_format="Blog Post",
            language="ko"
        )
        artifact_id = blog.get('artifact_id') if isinstance(blog, dict) else None
        log(f"  Artifact ID: {artifact_id}")

        output_file = "Tesla_Starlink_2026_Deep_Analysis_blog.md"
        log(f"  Waiting for generation (60s)...")
        time.sleep(60)

        for attempt in range(15):
            try:
                client.download_report(notebook_id, output_file, artifact_id)
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if len(content) < 100:
                    raise Exception("Content too short, not ready yet")

                log(f"\n{'='*70}")
                log("SUCCESS! Innovative Starlink Blog Generated")
                log(f"{'='*70}")
                log(f"  File: {output_file}")
                log(f"  Size: {len(content)} characters")
                log(f"  Sources Used: {len(sources) if sources else 'N/A'}")
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
print("Done! Check starlink_blog_log.txt")
