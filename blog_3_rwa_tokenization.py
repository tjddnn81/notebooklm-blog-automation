import os
import time
import sys
import traceback
from notebooklm_tools.core.auth import load_cached_tokens
from notebooklm_tools.core.client import NotebookLMClient

# --- Configuration ---
TOPIC = "2026 RWA 실물 자산 토큰화 혁명"
NOTEBOOK_TITLE = "RWA 토큰화 실물자산 투자 분석"
OUTPUT_FILENAME = "2026_RWA_Tokenization_blog.md"
LOG_FILENAME = "rwa_tokenization_blog_log.txt"

URL_SOURCES = [
    "https://namu.wiki/w/%EB%B8%94%EB%A1%9D%EC%B2%B4%EC%9D%B8",
    "https://namu.wiki/w/%ED%86%A0%ED%81%B0(%EC%95%94%ED%98%B8%ED%99%94%ED%8F%90)"
]

RESEARCH_QUERY = """
2026년 글로벌 금융 시장의 거대한 메가트렌드인 'RWA(Real World Assets, 실물 연계 자산) 토큰화'가 가져올 투자의 판도 변화를 심층 분석하는 블로그 포스트를 작성해줘.
독자들이 "아, 나도 빨리 커피값으로 강남 빌딩 조각 투자부터 알아봐야겠다"라고 바로 행동하게 만들 만큼 설득력 있고 매운맛(Spicy)의 톤앤매너로 작성할 것.

다음 핵심 요소들을 반드시 포함할 것:
1. **유동성의 해방과 그들만의 리그 붕괴**:
    - 강남 빌딩, 피카소 그림, 최고급 와인 등 수십~수백억대 자산가들만의 전유물이었던 고가 실물 자산들이 블록체인 스마트 컨트랙트를 만나 다이소 물건처럼 쪼개져 대중에게 풀리는 마법 같은 현실을 생생하게 설명.
2. **블랙록(BlackRock) 등 월스트리트 하이에나들의 움직임**:
    - 사기성 짙은 밈코인판과 선을 그으며, 왜 지금 세계 최대 자산운용사들이 미친 듯이 RWA 시장에 뛰어들고 미국 국채를 토큰화하는지 그 '진짜 이유(비용 절감, 즉각적 결제, 투명성)'를 알기 쉽게 풀이.
3. **가장 현실적인 RWA 실전 투자법 (Action Item)**:
    - 2026년 2030 세대 개인 투자자들이 현실적으로 접근할 수 있는 조각 투자(국채, 우량 부동산 등) 전략과 포트폴리오 다각화 관점에서의 마인드셋 제시.
4. **결론: 2026년형 넥스트 레벨 금융 민주화**:
    - 거대한 혁신에 올라타 내 장바구니에 프리미엄 자산 블록을 하나씩 담아가는 사람만이 자산 증식의 새로운 추월차선에 진입할 수 있음을 강렬하게 역설.

"비트코인 다음은 밈코인이 아닙니다. 10만 원으로 강남 꼬마빌딩 건물주가 되고, 스타벅스 커피값으로 미 국채 이자를 '매일' 받는 2026년 금융의 넥스트 레벨, RWA(실물 자산 토큰화)를 아시나요?"라는 강력한 어그로 훅으로 시작할 것. 철저하게 Markdown 포맷으로 작성해줘.
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
                footer = f"\n\n---\n*Generated by NotebookLM Automation (Topics: RWA Tokenization, Real World Assets)*"
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
