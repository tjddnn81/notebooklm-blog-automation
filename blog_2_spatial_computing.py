import os
import time
import sys
import traceback
from notebooklm_tools.core.auth import load_cached_tokens
from notebooklm_tools.core.client import NotebookLMClient

# --- Configuration ---
TOPIC = "2026 공간 컴퓨팅과 부동산 플랫폼 혁명"
NOTEBOOK_TITLE = "공간 컴퓨팅 랜선임장 인테리어 분석"
OUTPUT_FILENAME = "2026_Spatial_Computing_RealEstate_blog.md"
LOG_FILENAME = "spatial_computing_blog_log.txt"

URL_SOURCES = [
    "https://namu.wiki/w/%EA%B3%B5%EA%B0%84%20%EC%BB%B4%ED%93%A8%ED%8C%85",
    "https://namu.wiki/w/%ED%94%84%EB%A1%AD%ED%85%8C%ED%81%AC"
]

RESEARCH_QUERY = """
2026년 애플 비전 프로 등 혼합현실(XR) 기기의 대중화와 함께 본격화될 '공간 컴퓨팅(Spatial Computing)'이 부동산 및 인테리어 시장에 가져올 파괴적 혁신을 심층 분석하는 블로그 포스트를 작성해줘.
독자들이 "지금 당장 스마트 글래스 관련주를 사거나 프롭테크 트렌드를 공부해야겠다"라고 느낄 만큼 획기적이고 매콤한(Spicy) 톤앤매너로 작성할 것.

다음 핵심 요소들을 반드시 포함할 것:
1. **발품 임장의 종말과 초실감 랜선 임장의 진화**:
    - 허위 매물과 주말 발품에 지친 2030 세대의 해방. 방구석에서 스마트 글래스로 서울 강남 투룸부터 도쿄, 뉴욕의 아파트까지 100% 동일한 공간감으로 임장을 하는 사이버펑크틱한 시나리오 묘사.
2. **당근마켓과 가상 인테리어의 결합 (가심비 10만원 플랜테리어)**:
    - 중고 거래 앱에서 본 5만 원짜리 의자를 홀로그램으로 내 방 빈 공간에 미리 띄워보고, 햇빛의 방향에 따른 채광 시뮬레이션까지 확인 후 구매하는 일상의 변화.
3. **새로운 부의 기회 (Action Item)**:
    - 단순 사용자재의 편리함을 넘어 이 혁신을 주도하는 프롭테크(PropTech), 3D 스캐닝, 공간 데이터 관련 기업과 투자(ETF 등)의 폭발적 성장 가능성 제시.
4. **결론: 공간 제약을 벗어난 자의 특권**:
    - 미래에는 거실이 완벽한 부동산 중개소이자 최고급 쇼룸이 되며, 기술을 쓰는 자가 꿀매물을 선점함을 강조.

"주말마다 아파트 보러 다니며 차 막히고 시간 낭비하시나요? 2026년 2030 세대의 내 집 마련 필수 템은 스마트폰이 아닌 '스마트 글래스'입니다."라는 자극적인 어그로 훅으로 시작할 것. 철저하게 Markdown 포맷으로 작성해줘.
"""

def log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_FILENAME, "a", encoding="utf-8") as f:
        f.write(log_msg + "\n")

def main():
    log("======================================================================")
    log(f"프리미엄 블로그: {TOPIC}")
    log(f"날짜: {time.strftime('%Y-%m-%d')} | 전략: URL 소스 + Deep Research")
    log("======================================================================")

    try:
        tokens = load_cached_tokens()
        client = NotebookLMClient(cookies=tokens.cookies)
        log("[OK] Client initialized\n")

        log("[1/6] Creating notebook...")
        nb = client.create_notebook(NOTEBOOK_TITLE)
        notebook_id = getattr(nb, 'id', None) or getattr(nb, 'notebook_id', None) or str(nb)
        log(f"  Notebook ID: {notebook_id}\n")

        log("[2/6] Adding URL sources...")
        for i, url in enumerate(URL_SOURCES):
            try:
                client.add_url_source(notebook_id, url)
                log(f"  [{i+1}] OK: {url[:50]}...")
            except Exception as e:
                log(f"  [{i+1}] Error adding URL {url}: {e}")
        
        log(f"  Total URL sources: {len(URL_SOURCES)}")
        log("  Waiting for source processing (30s)...\n")
        time.sleep(30)

        log("[3/6] Starting deep research...")
        max_retries = 3
        task_id = None
        for attempt in range(max_retries):
            try:
                research = client.start_research(notebook_id, RESEARCH_QUERY, mode='deep')
                task_id = research.get('task_id') if isinstance(research, dict) else None
                log(f"  Task ID: {task_id}")
                break
            except Exception as e:
                log(f"  Attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    raise Exception("Failed to start research")
        log("\n")

        log("[4/6] Polling research status...")
        start_time = time.time()
        timeout = 1200
        sources = []
        while True:
            elapsed = int(time.time() - start_time)
            if elapsed > timeout:
                raise TimeoutError("Research timed out")
            try:
                poll = client.poll_research(notebook_id)
                if poll and isinstance(poll, dict):
                    state = poll.get('state') or poll.get('status')
                    sources = poll.get('sources') or poll.get('results') or []
                    if elapsed % 10 == 0:
                        print(f"\r  [{elapsed}s] state={state} sources={len(sources)}", end="", flush=True)
                    if state in ('completed', 'done') and len(sources) > 0:
                        print("")
                        log(f"  COMPLETED! Sources: {len(sources)}")
                        break
                    elif state and 'fail' in str(state).lower():
                        print("")
                        raise Exception(f"Research failed: {state}")
                time.sleep(5)
            except Exception as e:
                print("")
                log(f"  Polling error: {e}")
                time.sleep(10)
        log("\n")

        log("[5/6] Importing research sources...")
        if task_id:
             try:
                 client.import_research_sources(notebook_id, task_id, sources)
                 log(f"  Imported {len(sources)} research sources")
             except Exception as e:
                 log(f"  Import warning: {e}")
        time.sleep(10)
        log("\n")

        log("[6/6] Generating blog post...")
        try:
            blog = client.create_report(
                notebook_id=notebook_id,
                report_format="Blog Post",
                language="ko"
            )
            generation_id = blog.get('artifact_id') if isinstance(blog, dict) else getattr(blog, 'artifact_id', None)
            log(f"  Artifact ID: {generation_id}")
            log("  Waiting for generation (60s)...")
            time.sleep(60)

            report_content = None
            for i in range(15):
                try:
                    client.download_report(notebook_id, OUTPUT_FILENAME, generation_id)
                    if os.path.exists(OUTPUT_FILENAME):
                        with open(OUTPUT_FILENAME, 'r', encoding='utf-8') as f:
                            report_content = f.read()
                        if len(report_content) > 100:
                            break
                    else:
                         log(f"  Attempt {i+1}: file not created yet")
                except Exception as e:
                    log(f"  Attempt {i+1}: report not ready {e}")
                    time.sleep(10)

            if report_content:
                footer = f"\n\n---\n*Generated by NotebookLM Automation (Topics: Spatial Computing, PropTech)*"
                with open(OUTPUT_FILENAME, "a", encoding="utf-8") as f:
                    f.write(footer)
                print("")
                log("======================================================================")
                log("SUCCESS!")
                log(f"  File: {OUTPUT_FILENAME}")
                log(f"  Size: {len(report_content)} characters")
                log("======================================================================")
            else:
                 log("FAILED to download generated content.")
                 raise Exception("Content download failed")
        except Exception as e:
             log(f"Generation error: {e}")
             raise e

    except Exception as e:
        print("")
        log("======================================================================")
        log(f"ERROR: {str(e)}")
        log(traceback.format_exc())
        log("======================================================================")
        sys.exit(1)

if __name__ == "__main__":
    main()
