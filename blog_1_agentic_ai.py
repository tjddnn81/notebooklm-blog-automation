import os
import time
import sys
import traceback
from notebooklm_tools.core.auth import load_cached_tokens
from notebooklm_tools.core.client import NotebookLMClient

# --- Configuration ---
TOPIC = "2026 에이전틱 AI 무인 재테크"
NOTEBOOK_TITLE = "에이전틱 AI 무인 재테크 분석"
OUTPUT_FILENAME = "2026_Agentic_AI_Finance_blog.md"
LOG_FILENAME = "agentic_ai_finance_log.txt"

URL_SOURCES = [
    "https://namu.wiki/w/%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5",
    "https://namu.wiki/w/%EC%95%8C%EA%B3%A0%EB%A6%AC%EC%A6%98%20%ED%8A%B8%EB%A0%88%EC%9D%B4%EB%94%A9"
]

RESEARCH_QUERY = """
2026년 최신 글로벌 테크 및 금융 트렌드인 '에이전틱 AI(Agentic AI)'가 가져올 '무인 재테크' 혁명에 대해 심층 분석하는 블로그 포스트를 작성해줘.
단순 정보 전달을 넘어 "아, 세상이 이렇게 바뀌고 있구나! 당장 준비해야겠다!"라고 무릎을 탁 칠 만한 매콤하고(Spicy) 통찰력 있는 톤앤매너로 작성해야 해.

다음 핵심 요소들을 반드시 포함할 것:
1. **단순 챗봇의 종말과 에이전틱 AI의 등장**:
    - "삼성전자 살까?"에 대답만 하던 과거의 식상한 AI를 꼬집고, 내 목표 수익률에 맞춰 스스로 매수/매도 버튼까지 누르는 주도형 AI(Agentic AI)의 개념을 알기 쉽게 비유(내비게이션 vs 자율주행차 등)로 설명할 것.
2. **증권가 트레이더들의 현실과 퀀트 투자의 대중화**:
    - 월스트리트 기관 투자자들의 전유물이었던 퀀트 투자가 이제 일반 개인의 스마트폰 안으로 들어왔음을 선언.
    - 감정(탐욕과 공포)이 개입되지 않은 AI 기계적 매매의 압도적 우위 사례.
3. **일반인을 위한 실전 무인 재테크 세팅 가이드**:
    - 이 거대한 파도에 올라타기 위해 일반 투자자가 당장 실행해야 할 구체적이고 직관적인 액션 플랜 제시.
4. **결론: 2026년 자산 격차의 핵심**:
    - AI 비서를 고용하여 투자를 맡기는 자 vs AI와 맨몸으로 경쟁하는 자의 극명한 계좌 잔고 차이를 자극적으로 경고할 것.

"아직도 호가창 파란불 보며 심장 졸이시나요? 기관 최상위 트레이더의 뇌를 복사한 AI가 당신을 대신해 24시간 돈을 벌어옵니다."라는 뉘앙스의 강렬한 어그로 훅으로 시작할 것. 출력은 완벽한 Markdown 포맷으로 작성해줘.
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
                footer = f"\n\n---\n*Generated by NotebookLM Automation (Topics: Agentic AI, Quant Investing)*"
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
