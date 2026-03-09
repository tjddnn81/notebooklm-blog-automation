import os
import time
import sys
import traceback
from notebooklm_tools.core.auth import load_cached_tokens
from notebooklm_tools.core.client import NotebookLMClient

# --- Configuration ---
TOPIC = "제미나이 3.1 업데이트 완벽 분석"
NOTEBOOK_TITLE = "제미나이 3.1 업데이트"
OUTPUT_FILENAME = "Gemini_3.1_Update_blog.md"
LOG_FILENAME = "gemini_3.1_blog_log.txt"

# File Sources
FILE_SOURCES = [
    "Gemini_3.1_Source_Data.txt"
]

# Deep Research Query
RESEARCH_QUERY = """
최근 발표된 구글 제미나이(Gemini) 3.1 혹은 Agentic AI 업데이트에 대한 심층 분석 보고서를 작성해줘.
(Gemini 최신 버전, Agentic AI, 자율 에이전트 시대 개막 관련)
다음 핵심 요소들을 포함해야 해:

1. **제미나이 3.1 (혹은 최신 에이전트 업데이트) 핵심 기능**:
    - 개선된 추론 능력과 코딩 파트너로서의 진화.
    - 지시(Instruction)를 넘어 위임(Delegation)이 가능해진 Agentic Workflow.
    - 파일 시스템, 터미널 제어, 오류 자동 복구 기능.

2. **우리 일상과 업무의 변화**:
    - 리서치, 블로그 자동 생성, 코딩 자동화 등 킬러 활용 사례.
    - 개발자와 마케터/콘텐츠 크리에이터의 업무 방식 변화.

3. **향후 전망 및 유저 반응**:
    - AI가 수동적 도구에서 '능동적 동료'로 변화함에 따른 패러다임 시프트.
    - 글로벌 IT 업계의 트렌드 변화와 사람들의 기대감.

이 정보를 바탕으로, 사람들의 폭발적인 관심을 끌어낼 수 있는 "마침내 시작된 진짜 AI 동료의 시대"라는 서사를 갖춘 감동적이고 흡입력 있는 블로그 포스트를 생성해줘. (한국어, 이모티콘 활용, 가독성 높은 마크다운 형태)
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
    log(f"전략: Local File Source + Deep Research")
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
        notebook_id = getattr(nb, 'id', None) or getattr(nb, 'notebook_id', None) or str(nb)
        log(f"  Notebook ID: {notebook_id}")
        log("")

        # 3. Add File Sources
        log("[2/6] Adding File sources...")
        for i, file_path in enumerate(FILE_SOURCES):
            try:
                # Assuming client has add_file_source or similar method, 
                # or we just upload it if supported. As per NotebookLM MCP docs,
                # uploading files is the standard way. Let's use upload_document.
                # Actually, the python client method is likely upload_document
                client.add_file(notebook_id, file_path)
                log(f"  [{i+1}] OK: {file_path}")
            except Exception as e:
                log(f"  [{i+1}] Error adding File {file_path}: {e}")
        
        log(f"  Total File sources: {len(FILE_SOURCES)}")
        log("  Waiting for source processing (10s)...")
        time.sleep(10)
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
        timeout = 600  # 10 minutes
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
                    
                    if state in ('completed', 'done'):
                        print("") # New line
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

        # 6. Generate Blog Post
        log("[5/6] Generating blog post...")
        
        try:
            blog = client.create_report(
                notebook_id=notebook_id,
                report_format="Blog Post",
                language="ko"
            )
            
            generation_id = blog.get('artifact_id') if isinstance(blog, dict) else getattr(blog, 'artifact_id', None)
            
            log(f"  Artifact ID: {generation_id}")
            log("  Waiting for generation (30s)...")
            time.sleep(30)

            # 7. Download Content
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
                    if 'not ready' in str(e).lower():
                        time.sleep(15)
                    else:
                        log(f"  Attempt {i+1}: report not ready {e}")
                        time.sleep(15)

            if report_content:
                footer = f"\n\n---\n*Generated by NotebookLM with Deep Research.*"
                with open(OUTPUT_FILENAME, "a", encoding="utf-8") as f:
                    f.write(footer)
                
                print("")
                log("======================================================================")
                log("SUCCESS!")
                log("======================================================================")
                log(f"  File: {OUTPUT_FILENAME}")
                log(f"  Size: {len(report_content)} characters")
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
