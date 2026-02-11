#!/usr/bin/env python
"""AI 일자리 보호법 블로그 - 타임아웃 수정 버전"""
import os
import time

os.environ['NO_COLOR'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

log_file = open('ai_job_protection_log.txt', 'w', encoding='utf-8')

def log(msg):
    log_file.write(msg + '\n')
    log_file.flush()

log("=" * 70)
log("트렌드 블로그: AI 일자리 보호법 2026 총정리 (v2 - 타임아웃 수정)")
log("=" * 70)

try:
    from notebooklm_tools.core.auth import load_cached_tokens
    from notebooklm_tools.core.client import NotebookLMClient
    import httpx

    tokens = load_cached_tokens()
    # 타임아웃을 300초로 늘려서 클라이언트 생성
    client = NotebookLMClient(cookies=tokens.cookies)
    # httpx 클라이언트의 타임아웃 직접 수정
    if hasattr(client, '_client') or hasattr(client, 'client'):
        http_client = getattr(client, '_client', None) or getattr(client, 'client', None)
        if http_client and isinstance(http_client, httpx.Client):
            http_client._transport = httpx.HTTPTransport()
    log("[OK] Client initialized")

    # 쿼리를 간결하게 수정 (타임아웃 방지)
    query = '2026 AI 일자리 대체 보호법 현대 로봇 양산 미래 직업 전망 리스킬링'

    # 1. 노트북 생성
    log("\n[1/5] Creating notebook...")
    nb = client.create_notebook('AI_일자리보호법_2026')
    notebook_id = getattr(nb, 'id', None) or getattr(nb, 'notebook_id', None) or str(nb)
    log(f"  Notebook ID: {notebook_id}")

    # 2. Deep Research - 재시도 로직 추가
    log(f"\n[2/5] Starting deep research...")
    log(f"  Query: {query}")
    
    research = None
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
        log("  All retries failed!")
        raise Exception("start_research failed after 3 retries")

    # 3. 완료 대기
    log("\n[3/5] Polling research status...")
    max_wait = 480
    start = time.time()
    completed = False
    sources = None

    while time.time() - start < max_wait:
        try:
            poll = client.poll_research(notebook_id)
            if poll and isinstance(poll, dict):
                state = poll.get('state') or poll.get('status')
                sources = poll.get('sources') or poll.get('results')

                if state == 'completed' or state == 'done' or sources:
                    log(f"  COMPLETED! Sources: {len(sources) if sources else 0}")
                    completed = True
                    break
                elif 'fail' in str(state).lower():
                    log(f"  FAILED: {state}")
                    break

            elapsed = int(time.time() - start)
            log(f"  Waiting... ({elapsed}s)")
            time.sleep(25)
        except Exception as e:
            log(f"  Warning: {e}")
            time.sleep(25)

    if not completed:
        log("  TIMEOUT - continuing anyway")

    # 4. 소스 임포트
    log("\n[4/5] Importing sources...")
    if sources and task_id:
        try:
            client.import_research_sources(notebook_id, task_id, sources)
            log(f"  Imported {len(sources)} sources")
        except Exception as e:
            log(f"  Warning: {e}")

    # 5. 블로그 생성
    log("\n[5/5] Generating Korean blog...")
    try:
        blog = client.create_report(
            notebook_id=notebook_id,
            report_format="Blog Post",
            language="ko"
        )
        artifact_id = blog.get('artifact_id') if isinstance(blog, dict) else None
        log(f"  Artifact ID: {artifact_id}")

        output_file = "AI_일자리_보호법_2026_총정리_blog.md"
        log("  Waiting for generation (60s)...")
        time.sleep(60)

        for attempt in range(15):
            try:
                client.download_report(notebook_id, output_file, artifact_id)
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                log(f"\n{'='*70}")
                log("SUCCESS!")
                log(f"{'='*70}")
                log(f"  File: {output_file}")
                log(f"  Size: {len(content)} characters")
                log(f"  Sources: {len(sources) if sources else 'N/A'}")
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
print("Done! Check ai_job_protection_log.txt")
