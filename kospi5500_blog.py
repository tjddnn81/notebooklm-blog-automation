#!/usr/bin/env python
"""코스피 5500 돌파 & 곱버스 대참사 블로그 생성 (2026.02.18)"""
import os
import time

os.environ['NO_COLOR'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

log_file = open('kospi5500_blog_log.txt', 'w', encoding='utf-8')

def log(msg):
    log_file.write(msg + '\n')
    log_file.flush()
    print(msg)

log("=" * 70)
log("프리미엄 블로그: 코스피 5500 돌파 & 곱버스 대참사 분석")
log("날짜: 2026-02-18 | 전략: URL 소스 + Deep Research")
log("=" * 70)

try:
    from notebooklm_tools.core.auth import load_cached_tokens
    from notebooklm_tools.core.client import NotebookLMClient

    tokens = load_cached_tokens()
    client = NotebookLMClient(cookies=tokens.cookies)
    log("[OK] Client initialized")

    # 1. Notebook 생성
    log("\n[1/6] Creating notebook...")
    nb = client.create_notebook("KOSPI_5500_InverseETF_2026")
    notebook_id = getattr(nb, 'id', None) or getattr(nb, 'notebook_id', None) or str(nb)
    log(f"  Notebook ID: {notebook_id}")

    # 2. URL 소스 추가 (핵심 참고자료)
    log("\n[2/6] Adding URL sources...")
    urls = [
        "https://namu.wiki/w/KODEX%20200%EC%84%A0%EB%AC%BC%EC%9D%B8%EB%B2%84%EC%8A%A42X",
        "https://namu.wiki/w/KOSPI",
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

    log(f"  Total URL sources: {added}")

    if added > 0:
        log("  Waiting for source processing (30s)...")
        time.sleep(30)

    # 3. Deep Research - 코스피 5500 & 곱버스 다각도 분석
    log("\n[3/6] Starting deep research...")
    # 왜: 다각도 쿼리로 차별화된 고품질 블로그를 위해 넓은 범위의 소스 확보
    query = """코스피 KOSPI 5500 돌파 사상 최고치 2026년 2월 원인 분석 반도체 삼성전자 SK하이닉스
코스피 5500 이후 전망 증권사 목표 6000 언제 달성 가능성 전문가 의견
곱버스 KODEX 인버스 2X ETF 대폭락 손실 규모 투자자 피해 사례 2026
곱버스 인버스 ETF 원리 구조 레버리지 복리 효과 장기 보유 위험성 설명
코스피 급등 원인 AI 반도체 수출 호조 외국인 매수 원화 강세 정부 정책
코스피 5500 시대 개인 투자자 대응 전략 포트폴리오 리밸런싱 방법
곱버스 물린 사람 손절 타이밍 대처법 인버스 탈출 전략 손실 만회
한국 증시 역사 코스피 1000 2000 3000 4000 5000 돌파 타임라인
미국 관세 25% 위협 한국 증시 영향 트럼프 무역전쟁 코스피 변동성
2026년 하반기 증시 전망 금리 인하 AI 테마주 배당주 추천"""

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

    if not research:
        raise Exception("start_research failed after 3 retries")

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
                    log(f"  COMPLETED! Sources: {len(sources)}")
                    completed = True
                    break
                elif state and 'fail' in str(state).lower():
                    log(f"  FAILED: {state}")
                    break

            time.sleep(10)
        except Exception as e:
            log(f"  Warning: {e}")
            time.sleep(15)

    if not completed:
        log("  TIMEOUT - proceeding with URL sources only")

    # 5. 소스 임포트
    log("\n[5/6] Importing research sources...")
    if completed and sources and task_id:
        try:
            client.import_research_sources(notebook_id, task_id, sources)
            log(f"  Imported {len(sources)} research sources")
        except Exception as e:
            log(f"  Warning importing: {e}")
    else:
        log(f"  Using {added} URL sources only")

    # 6. 블로그 생성
    log("\n[6/6] Generating blog post...")
    try:
        blog = client.create_report(
            notebook_id=notebook_id,
            report_format="Blog Post",
            language="ko"
        )
        artifact_id = blog.get('artifact_id') if isinstance(blog, dict) else None
        log(f"  Artifact ID: {artifact_id}")

        output_file = "KOSPI_5500_곱버스_대참사_2026_blog.md"
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
print("Done! Check kospi5500_blog_log.txt")
