import os
import sys
import time

# NotebookLM MCP Client
from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
TOPIC = "2026년 폭발적 핵심 트렌드: AI 에이전트(노비서) 활용 1인 기업으로 월 1천만 원 자동 수익화 완벽 가이드"
NOTEBOOK_TITLE = "Trend_2026_AI_Monetization"
OUTPUT_FILENAME = "AI_Agent_Monetization_2026_blog.md"
LOG_FILENAME = "special_trend_blog_log.txt"

# File Sources
FILE_SOURCES = [
    r"d:\자동화\노트북LM 파트\Trending_AI_Money_Source.txt"
]

# Deep Research Query
RESEARCH_QUERY = f"""
다음은 2026년 최신 비즈니스 핵심 트렌드인 'AI 에이전트를 활용한 1인 기업 자동화 수익 창출'에 대한 소스 데이터입니다.
이 데이터를 바탕으로 사람들의 이목을 한눈에 집중시킬 수 있는 고품질의 블로그 포스트를 작성해 주세요.

[요구사항]
1. 제목: 검색에 잘 걸리고 사람들의 클릭을 유도할 수 있는 자극적이고 매우 매력적인 "폭발적"인 제목으로 작성해 주세요. (예: 2026년 당신만 모르는 AI 노비서 1인 기업으로 월 1천만원 자동 수익 만들기)
2. 내용 구성: 서론(현 상황의 패러다임 전환), 4가지 핵심 자동화 수익 모델 상세 설명, 성공 사례, 당장 시작할 수 있는 3단계 액션 플랜, 그리고 결론.
3. 톤 앤 매너: 독자에게 바로 행동을 촉구하는 강력하고 확신에 찬 어조, '노비서', '바이브 코딩', '자동화 수익' 같은 핵심 키워드를 강조.
4. 포맷: Markdown 형식(제목별 H2, H3 태그, 글머리 기호 사용)으로 가독성 극대화. 중요 문구는 볼드 처리.
5. 주의: 없는 내용을 지어내지 말고 제공된 소스를 기반으로 설득력 있고 전문적으로 작성할 것. 마무리는 강렬한 테이크아웃(요약)을 넣어주세요.
"""

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")
    with open(LOG_FILENAME, 'a', encoding='utf-8') as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def main():
    log("======================================================================")
    log(f"스페셜 트렌드 블로그: {TOPIC}")
    log(f"전략: Local File Source + Deep Research")
    log("======================================================================")

    try:
        # Initialize client
        tokens = load_cached_tokens()
        client = NotebookLMClient(cookies=tokens.cookies)
        log("[OK] Client initialized")
        log("")

        # 1. Create Notebook
        log("[1/6] Creating notebook...")
        notebook = client.create_notebook(NOTEBOOK_TITLE)
        notebook_id = getattr(notebook, 'id', None) or getattr(notebook, 'notebook_id', None) or str(notebook)
        if not notebook_id:
            raise ValueError(f"Failed to get notebook ID from response: {notebook}")
        log(f"  Notebook ID: {notebook_id}")
        log("")

        # 2. Add File Sources
        log("[2/6] Adding File sources...")
        for i, file_path in enumerate(FILE_SOURCES):
            try:
                client.add_file(notebook_id, file_path)
                log(f"  [{i+1}] OK: {file_path}")
            except Exception as e:
                log(f"  [{i+1}] Error adding File {file_path}: {e}")
        
        log(f"  Total File sources: {len(FILE_SOURCES)}")
        log("  Waiting for source processing (10s)...")
        time.sleep(10)
        log("")

        # 3. Starting Deep Research
        log("[3/6] Starting deep research...")
        client.start_research(notebook_id, RESEARCH_QUERY, mode='deep')
        log("")

        # 4. Polling Research Status
        log("[4/6] Polling research status...")
        start_time = time.time()
        timeout = 600
        
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
                        sys.stdout.write(f"\r  [{elapsed}s] state={state} sources={len(sources)}")
                        sys.stdout.flush()
                    
                    if state in ('completed', 'done'):
                        print("")
                        log(f"  COMPLETED!")
                        break
                    elif state and 'fail' in str(state).lower():
                        print("")
                        raise Exception(f"Research failed: {state}")
                    
                time.sleep(10)
            except Exception as e:
                print("")
                log(f"  Polling error: {e}")
                time.sleep(10)
        log("")

        # 5. Generating Blog Post
        log("[5/6] Generating blog post...")
        blog = client.create_report(
            notebook_id=notebook_id,
            report_format="Blog Post",
            language="ko"
        )
        
        generation_id = blog.get('artifact_id') if isinstance(blog, dict) else getattr(blog, 'artifact_id', None)
        log(f"  Artifact ID: {generation_id}")
        log("  Waiting for generation (30s)...")
        time.sleep(30) # Let it brew

        # 6. Downloading Content
        log("[6/6] Downloading blog post...")
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
                time.sleep(15)
        
        if not report_content:
            log("[ERROR] Received empty content or timed out.")
            return

        with open(OUTPUT_FILENAME, "a", encoding="utf-8") as f:
            f.write("\n\n---\n*Generated by NotebookLM Auto-system.*")
            
        log("")
        log("======================================================================")
        log("SUCCESS!")
        log("======================================================================")
        log(f"  File: {OUTPUT_FILENAME}")
        log(f"  Size: {len(report_text)} characters")

    except Exception as e:
        log("")
        log(f"[FATAL ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
