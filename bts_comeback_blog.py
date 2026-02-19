import os
import time
import sys
import traceback
from notebooklm_tools.core.auth import load_cached_tokens
from notebooklm_tools.core.client import NotebookLMClient

# --- Configuration ---
TOPIC = "BTS 2026 Forever Comeback"
NOTEBOOK_TITLE = "BTS 2026 완전체 컴백 분석"
OUTPUT_FILENAME = "BTS_Comeback_2026_blog.md"
LOG_FILENAME = "bts_comeback_log.txt"

# URL Sources (Namu Wiki or Official)
URL_SOURCES = [
    "https://namu.wiki/w/%EB%B0%A9%ED%83%84%EC%86%8C%EB%85%84%EB%8B%A8", # BTS Namu Wiki
    "https://namu.wiki/w/%EB%B0%A9%ED%83%84%EC%86%8C%EB%85%84%EB%8B%A8/%EC%97%AD%EC%82%AC" # BTS History
]

# Deep Research Query (Comprehensive & "Explosive")
RESEARCH_QUERY = """
2026년 3월 방탄소년단(BTS) 완전체 컴백에 대한 심층 분석 보고서를 작성해줘.
다음 핵심 요소들을 포함해야 해:

1. **'ARIRANG' 앨범 및 컴백 디테일**:
    - 2026년 3월 20일 발매되는 새 앨범 'ARIRANG'의 컨셉과 의미.
    - 3월 21일 서울 광화문광장에서 열리는 'BTS THE COMEBACK LIVE: ARIRANG' 공연 상세 내용과 넷플릭스 생중계 파급력.
    - 타이틀곡 및 수록곡 정보, 뮤직비디오 컨셉.

2. **2026-2027 월드투어 'Arirang World Tour'**:
    - 4월 9일 고양 스타디움을 시작으로 하는 투어 일정 및 규모 (34개 도시, 82회 공연).
    - 티켓팅 대란 현황 (Ticketmaster 매진 기록 등) 및 다이내믹 프라이싱 논란 여부.
    - 예상 관객 수 및 티켓 매출 규모.

3. **경제적 파급 효과 (하이브 & 한국 경제)**:
    - HYBE 주가 전망 (증권가 목표 주가 50만 원 상향 리포트 인용).
    - BTS 컴백이 가져올 경제적 낙수 효과 (관광, 숙박, 면세 등).
    - 'BTS 효과'로 인한 K-컬처 재도약 전망.

4. **팬덤 '아미(ARMY)'의 반응 및 문화적 현상**:
    - '보라해(I Purple You)' 10주년과 맞물린 팬덤의 결집력.
    - 전 세계 아미들의 컴백 기대 반응 및 소셜 미디어 트렌드.

5. **멤버별 군 전역 후 변화 및 성장**:
    - 군 백기 동안 각 멤버들의 솔로 활동 성과와 성장 포인트가 완전체 시너지에 미치는 영향.

이 정보를 바탕으로, 단순한 뉴스 전달이 아닌 "왕의 귀환"이라는 서사를 갖춘 감동적이고 폭발적인 블로그 포스트를 생성해줘.
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
        # 1. Initialize Client
        tokens = load_cached_tokens()
        client = NotebookLMClient(cookies=tokens.cookies)
        log("[OK] Client initialized")
        log("")

        # 2. Create Notebook
        log("[1/6] Creating notebook...")
        nb = client.create_notebook(NOTEBOOK_TITLE)
        # Notebook object handling might vary, standardizing to ID extraction
        notebook_id = getattr(nb, 'id', None) or getattr(nb, 'notebook_id', None) or str(nb)
        log(f"  Notebook ID: {notebook_id}")
        log("")

        # 3. Add URL Sources
        log("[2/6] Adding URL sources...")
        for i, url in enumerate(URL_SOURCES):
            try:
                client.add_url_source(notebook_id, url)
                log(f"  [{i+1}] OK: {url[:50]}...")
            except Exception as e:
                log(f"  [{i+1}] Error adding URL {url}: {e}")
        
        log(f"  Total URL sources: {len(URL_SOURCES)}")
        log("  Waiting for source processing (30s)...")
        time.sleep(30)
        log("")

        # 4. Starting Deep Research
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
                    raise Exception("Failed to start research after multiple attempts")
        log("")

        # 5. Polling Research Status
        log("[4/6] Polling research status...")
        start_time = time.time()
        timeout = 1200  # 20 minutes
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
                        print("") # New line
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
        log("")

        # 6. Import Research Sources (if needed, mainly for reference, NotebookLM might auto-add)
        log("[5/6] Importing research sources...")
        if task_id:
             try:
                 client.import_research_sources(notebook_id, task_id, sources)
                 log(f"  Imported {len(sources)} research sources")
             except Exception as e:
                 log(f"  Import warning: {e}")

        time.sleep(10)
        log("")

        # 7. Generate Blog Post
        log("[6/6] Generating blog post...")
        
        try:
            # Reverting to create_report instead of generate_content since the client doesn't support generate_content directly
            # We hope create_report uses the accumulated sources well enough.
            # To mitigate quality loss, we rely on the detailed Query we used for Deep Research.
            blog = client.create_report(
                notebook_id=notebook_id,
                report_format="Blog Post",
                language="ko"
            )
            
            # Extract artifact ID safely
            generation_id = blog.get('artifact_id') if isinstance(blog, dict) else getattr(blog, 'artifact_id', None)
            
            log(f"  Artifact ID: {generation_id}")
            log("  Waiting for generation (60s)...")
            time.sleep(60)

            # 8. Download Content
            report_content = None
            for i in range(15):
                try:
                    # Using download_report for consistency
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
                # Append footer
                footer = f"\n\n---\n*Generated by NotebookLM with {len(sources)} Deep Research sources & {len(URL_SOURCES)} URL sources.*"
                with open(OUTPUT_FILENAME, "a", encoding="utf-8") as f:
                    f.write(footer)
                
                print("")
                log("======================================================================")
                log("SUCCESS!")
                log("======================================================================")
                log(f"  File: {OUTPUT_FILENAME}")
                log(f"  Size: {len(report_content)} characters")
                log(f"  URL Sources: {len(URL_SOURCES)}")
                log(f"  Research Sources: {len(sources)}")
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
