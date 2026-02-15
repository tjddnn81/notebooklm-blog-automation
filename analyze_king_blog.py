#!/usr/bin/env python
"""King and the Man Movie Blog Analysis Script - 2026.02.15"""
import os
import time

os.environ['NO_COLOR'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

log_file = open('king_blog_log.txt', 'w', encoding='utf-8')

def log(msg):
    log_file.write(msg + '\n')
    log_file.flush()
    print(msg)

log("=" * 70)
log("트렌드 블로그: 영화 '왕과 사는 남자' (임금님과 사는 남자) 역사 팩트체크")
log("주제: 단종 유배지 영월 청령포, 엄흥도 실존 인물, 한명회 야사 분석")
log("=" * 70)

try:
    from notebooklm_tools.core.auth import load_cached_tokens
    from notebooklm_tools.core.client import NotebookLMClient
    import httpx

    tokens = load_cached_tokens()
    client = NotebookLMClient(cookies=tokens.cookies)
    
    # Increase timeout
    if hasattr(client, '_client') or hasattr(client, 'client'):
        http_client = getattr(client, '_client', None) or getattr(client, 'client', None)
        if http_client and isinstance(http_client, httpx.Client):
            http_client._transport = httpx.HTTPTransport()
            
    log("[OK] Client initialized")

    # Topic with YouTube link and detailed historical query
    youtube_url = "https://youtu.be/w1Qdvj--CVE?si=KicZW4F0AEvXb18U"
    topic = {
        'name': 'Movie_King_and_Man_History_Analysis',
        'query': f'''영화 '왕과 사는 남자' (임금님과 사는 남자) 줄거리 및 역사적 배경 분석
유튜브 영상 분석: {youtube_url}
단종(이홍위) 유배 생활 영월 청령포 실제 역사 기록 (조선왕조실록)
엄흥도(영월 호장)가 목숨 걸고 단종 시신 수습한 실화 (충신 엄흥도)
계유정난 이후 한명회 권력 장악과 단종 폐위 과정 팩트체크
영화 속 허구와 실제 역사의 차이점 (엄흥도와 단종의 동거 여부 등)
배우 박지훈(단종), 유해진(엄흥도), 유지태(한명회) 캐스팅 및 캐릭터 분석
단종애사 야사 및 전설 (청령포 소나무, 관음송 이야기)''',
    }

    # 1. Create Notebook
    log("\n[1/5] Creating notebook...")
    try:
        nb = client.create_notebook(topic['name'][:40])
        notebook_id = getattr(nb, 'id', None) or getattr(nb, 'notebook_id', None) or str(nb)
        log(f"  Notebook ID: {notebook_id}")
    except Exception as e:
        log(f"  ERROR: {e}")
        raise

    # 2. Start Deep Research (Focus on historical depth)
    log(f"\n[2/5] Starting deep research (Historical Fact-Check)...")
    log(f"  Query: {topic['query'][:80]}...")
    
    research = None
    for retry in range(3):
        try:
            research = client.start_research(
                notebook_id=notebook_id,
                query=topic['query'],
                mode='deep'  # Deep mode for historical accuracy
            )
            task_id = research.get('task_id') if isinstance(research, dict) else None
            log(f"  Task ID: {task_id}")
            break
        except Exception as e:
            log(f"  Retry {retry+1}/3: {e}")
            time.sleep(10)
    
    if not research:
        raise Exception("start_research failed after 3 retries")

    # 3. Poll for Completion
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
                
                if sources:
                   print(f"  Collecting sources... Current count: {len(sources)}", end='\r')

            elapsed = int(time.time() - start)
            if elapsed % 30 == 0:
                log(f"  Waiting... ({elapsed}s)")
            time.sleep(10)

        except Exception as e:
            log(f"  Warning polling: {e}")
            time.sleep(20)

    if not completed:
        log("  TIMEOUT - attempting to proceed with whatever sources we have")

    # 4. Import Sources
    log("\n[4/5] Importing sources...")
    if sources and task_id:
        try:
            client.import_research_sources(notebook_id, task_id, sources)
            log(f"  Imported {len(sources)} sources")
        except Exception as e:
            log(f"  Warning importing: {e}")

    # 5. Generate Blog
    log("\n[5/5] Generating historical fact-check blog...")
    try:
        report_title = "영화 '왕과 사는 남자' vs 실제 역사: 단종과 엄흥도의 진실"
        blog = client.create_report(
            notebook_id=notebook_id,
            report_format="Blog Post",
            language="ko"
        )
        artifact_id = blog.get('artifact_id') if isinstance(blog, dict) else None
        log(f"  Artifact ID: {artifact_id}")

        output_file = "King_and_Man_History_FactCheck_blog.md"
        log(f"  Waiting for generation (60s)...")
        time.sleep(60)

        for attempt in range(15):
            try:
                client.download_report(notebook_id, output_file, artifact_id)
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if len(content) < 100:
                    raise Exception("Content too short, maybe not ready")

                log(f"\n{'='*70}")
                log("SUCCESS! Historical Blog Generated")
                log(f"{'='*70}")
                log(f"  File: {output_file}")
                log(f"  Size: {len(content)} characters")
                log(f"  Sources Used: {len(sources) if sources else 'N/A'}")
                break
            except Exception as e:
                log(f"  Attempt {attempt+1}: {e}")
                time.sleep(20)

    except Exception as e:
        log(f"  ERROR during content generation: {e}")
        import traceback
        log(traceback.format_exc())

except Exception as e:
    log(f"FATAL ERROR: {e}")
    import traceback
    log(traceback.format_exc())

log_file.close()
log("Done! Check king_blog_log.txt")
