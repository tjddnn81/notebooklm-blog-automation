#!/usr/bin/env python
"""Tesla Starlink Blog V2 - 개인 사용자 관점 완전 가이드 (2026.02.16)"""
import os
import time

os.environ['NO_COLOR'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

log_file = open('starlink_v2_log.txt', 'w', encoding='utf-8')

def log(msg):
    log_file.write(msg + '\n')
    log_file.flush()
    print(msg)

log("=" * 70)
log("프리미엄 블로그: 스타링크 개인사용자 완전정복 가이드 V2")
log("날짜: 2026-02-16 | 관점: 개인 사용자, 가입방법, 설정, 활용법")
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

    # 개인 사용자 관점의 쿼리 - 실용적이고 구체적인 정보
    topic = {
        'name': 'Starlink_Personal_User_Guide_2026',
        'query': '''스타링크 개인 사용자 가입 방법 2026 한국 주문 절차 상세 가이드 (starlink.com 회원가입부터 배송까지)
스타링크 개인용 요금제 종류 비교 2026 (Residential Standard, Residential Priority, Roam, Boat, 미니 Mini)
스타링크 키트 구성품 개봉기 (안테나 디쉬, Wi-Fi 라우터, 케이블, 마운트) 하드웨어 스펙
스타링크 초기 설정 방법 앱 다운로드 설치 과정 (Starlink 앱 iOS Android 연결 WiFi 설정)
스타링크 안테나 설치 위치 선정 방법 (장애물 회피, 하늘 시야각 확보, 지붕 설치 팁)
스타링크가 필요한 사람들 (시골 농촌 산간지역 거주자, 캠핑카 차박 여행자, 해외 원격근무자, 섬 거주민)
스타링크 실제 사용 후기 속도 테스트 (다운로드 업로드 속도, 레이턴시, 게임 가능 여부)
스타링크 vs 국내 통신사 KT SKT LG 인터넷 비교 (속도, 가격, 안정성, 설치 난이도)
스타링크 Roam 이동형 요금제 캠핑 차박 활용법 (이동 중 사용, 해외 로밍)
스타링크 단점 한계 솔직 리뷰 (날씨 영향, 나무 장애물, 속도 저하 시간대, 데이터 제한)''',
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

    # 2. Deep Research
    log(f"\n[2/5] Starting deep research (Personal User Focus)...")
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
    log("\n[5/5] Generating personal user guide blog...")
    try:
        blog = client.create_report(
            notebook_id=notebook_id,
            report_format="Blog Post",
            language="ko"
        )
        artifact_id = blog.get('artifact_id') if isinstance(blog, dict) else None
        log(f"  Artifact ID: {artifact_id}")

        output_file = "Starlink_개인사용자_완전정복_가이드_blog.md"
        log(f"  Waiting for generation (60s)...")
        time.sleep(60)

        success = False
        for attempt in range(15):
            try:
                client.download_report(notebook_id, output_file, artifact_id)
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if len(content) < 100:
                    raise Exception("Content too short, not ready yet")

                log(f"\n{'='*70}")
                log("SUCCESS! Personal User Guide Blog Generated")
                log(f"{'='*70}")
                log(f"  File: {output_file}")
                log(f"  Size: {len(content)} characters")
                log(f"  Sources Used: {len(sources) if sources else 'N/A'}")
                success = True
                break
            except Exception as e:
                log(f"  Attempt {attempt+1}: {e}")
                time.sleep(20)

        if not success:
            log("  FAILED to download blog after 15 attempts")

    except Exception as e:
        log(f"  ERROR: {e}")
        import traceback
        log(traceback.format_exc())

except Exception as e:
    log(f"FATAL ERROR: {e}")
    import traceback
    log(traceback.format_exc())

log_file.close()
print("Done! Check starlink_v2_log.txt")
