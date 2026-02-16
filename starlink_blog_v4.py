#!/usr/bin/env python
"""Starlink Blog V4 - 개인사용자 완전정복 (올바른 API 사용)"""
import os
import time

os.environ['NO_COLOR'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

log_file = open('starlink_v4_log.txt', 'w', encoding='utf-8')

def log(msg):
    log_file.write(msg + '\n')
    log_file.flush()
    print(msg)

log("=" * 70)
log("프리미엄 블로그: 스타링크 개인사용자 완전정복 가이드 V4")
log("전략: add_url_source (올바른 API) + Deep Research")
log("=" * 70)

try:
    from notebooklm_tools.core.auth import load_cached_tokens
    from notebooklm_tools.core.client import NotebookLMClient

    tokens = load_cached_tokens()
    client = NotebookLMClient(cookies=tokens.cookies)
    log("[OK] Client initialized")

    # 1. Notebook 생성
    log("\n[1/6] Creating notebook...")
    nb = client.create_notebook("Starlink_Personal_Guide_V4")
    notebook_id = getattr(nb, 'id', None) or getattr(nb, 'notebook_id', None) or str(nb)
    log(f"  Notebook ID: {notebook_id}")

    # 2. URL 소스 직접 추가 (올바른 메서드: add_url_source)
    log("\n[2/6] Adding URL sources (add_url_source)...")
    urls = [
        "https://www.starlink.com/residential",
        "https://www.starlink.com/roam",
        "https://namu.wiki/w/%EC%8A%A4%ED%83%80%EB%A7%81%ED%81%AC(%EC%9C%84%EC%84%B1%20%EC%9D%B8%ED%84%B0%EB%84%B7)",
    ]

    added = 0
    for url in urls:
        try:
            client.add_url_source(notebook_id, url)
            added += 1
            log(f"  [{added}] OK: {url[:60]}...")
            time.sleep(3)
        except Exception as e:
            log(f"  SKIP: {url[:50]}... -> {e}")
            time.sleep(2)

    log(f"  Total URL sources added: {added}")

    # 소스 준비 대기
    if added > 0:
        log("  Waiting for sources to be processed (30s)...")
        time.sleep(30)

    # 3. Deep Research (개인 사용자 관점)
    log("\n[3/6] Starting deep research (Personal User Focus)...")
    query = """스타링크 개인사용자 가입방법 상세 절차 2026 한국 starlink.com 주문
스타링크 요금제 종류 비교 Residential Standard Priority Roam Mini 가격
스타링크 키트 구성품 안테나 디쉬 라우터 케이블 마운트 개봉기
스타링크 앱 설치 초기 설정 방법 WiFi 연결 가이드 iOS Android
스타링크 안테나 설치 위치 선정 하늘 시야각 장애물 회피 지붕 설치 팁
스타링크 누구에게 필요한가 시골 농촌 산간 캠핑카 차박 섬 해외 원격근무
스타링크 실사용 후기 속도 테스트 다운로드 업로드 핑 게임 스트리밍
스타링크 단점 한계 날씨 영향 비 눈 나무 장애물 속도 저하 피크타임"""

    research = None
    task_id = None
    for retry in range(3):
        try:
            research = client.start_research(
                notebook_id=notebook_id,
                query=query,
                mode='deep'
            )
            task_id = research.get('task_id') if isinstance(research, dict) else None
            log(f"  Task ID: {task_id}")
            break
        except Exception as e:
            log(f"  Retry {retry+1}/3: {e}")
            time.sleep(10)

    # 4. 폴링 (최대 8분)
    log("\n[4/6] Polling research status...")
    max_wait = 480
    start = time.time()
    completed = False
    sources = None

    while time.time() - start < max_wait:
        try:
            poll = client.poll_research(notebook_id)
            if poll and isinstance(poll, dict):
                state = poll.get('state') or poll.get('status')
                sources = poll.get('sources') or poll.get('results') or []

                elapsed = int(time.time() - start)
                if elapsed % 30 == 0:
                    log(f"  [{elapsed}s] state={state} sources={len(sources) if sources else 0}")

                if state in ('completed', 'done') and len(sources) > 0:
                    log(f"  COMPLETED! Research sources: {len(sources)}")
                    completed = True
                    break
                elif state and 'fail' in str(state).lower():
                    log(f"  FAILED: {state}")
                    break

            time.sleep(10)
        except Exception as e:
            log(f"  Warning: {e}")
            time.sleep(15)

    # 5. 리서치 소스 임포트
    log("\n[5/6] Importing research sources...")
    if completed and sources and task_id:
        try:
            client.import_research_sources(notebook_id, task_id, sources)
            log(f"  Imported {len(sources)} research sources")
        except Exception as e:
            log(f"  Warning importing: {e}")
    else:
        log(f"  Research did not complete. Using {added} URL sources only.")

    # 6. 블로그 생성
    log("\n[6/6] Generating personal user guide blog...")
    try:
        blog = client.create_report(
            notebook_id=notebook_id,
            report_format="Blog Post",
            language="ko"
        )
        artifact_id = blog.get('artifact_id') if isinstance(blog, dict) else None
        log(f"  Artifact ID: {artifact_id}")

        output_file = "Starlink_개인사용자_완전정복_가이드_blog.md"
        log("  Waiting for generation (60s)...")
        time.sleep(60)

        success = False
        for attempt in range(15):
            try:
                client.download_report(notebook_id, output_file, artifact_id)
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if len(content) < 100:
                    raise Exception("Content too short")

                log(f"\n{'='*70}")
                log("SUCCESS!")
                log(f"{'='*70}")
                log(f"  File: {output_file}")
                log(f"  Size: {len(content)} characters")
                log(f"  URL Sources: {added}")
                log(f"  Research Sources: {len(sources) if sources else 0}")
                success = True
                break
            except Exception as e:
                log(f"  Attempt {attempt+1}: {e}")
                time.sleep(20)

        if not success:
            log("  FAILED to download after 15 attempts")

    except Exception as e:
        log(f"  ERROR: {e}")
        import traceback
        log(traceback.format_exc())

except Exception as e:
    log(f"FATAL ERROR: {e}")
    import traceback
    log(traceback.format_exc())

log_file.close()
print("Done! Check starlink_v4_log.txt")
