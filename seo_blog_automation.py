#!/usr/bin/env python
"""Create 3 SEO-optimized blogs with evergreen + trending topics."""
import os
import time

os.environ['NO_COLOR'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

log_file = open('seo_blog_log.txt', 'w', encoding='utf-8')

def log(msg):
    log_file.write(msg + '\n')
    log_file.flush()

log("=" * 70)
log("SEO 최적화 블로그 3개 자동 생성")
log("주제 유형: 에버그린 + How-to + 제품 리뷰")
log("=" * 70)

try:
    from notebooklm_tools.core.auth import load_cached_tokens
    from notebooklm_tools.core.client import NotebookLMClient
    
    tokens = load_cached_tokens()
    client = NotebookLMClient(cookies=tokens.cookies)
    log("[OK] Client initialized")
    
    # SEO 최적화 주제 3개 (에버그린 + 높은 검색량)
    topics = [
        {
            'name': 'ChatGPT_업무_활용법_완벽가이드',
            'query': 'ChatGPT 업무 활용법 프롬프트 작성법 이메일 보고서 회의록 요약 생산성 향상 꿀팁 2026',
            'type': 'How-to Guide'
        },
        {
            'name': '갤럭시S26울트라_카메라_설정_꿀팁',
            'query': '갤럭시 S26 울트라 카메라 설정 야간모드 인물사진 200MP 촬영 꿀팁 사진 잘찍는법 2026',
            'type': 'Product Review'
        },
        {
            'name': '2026년_부업_추천_월100만원',
            'query': '2026년 부업 추천 월 100만원 재택근무 투잡 N잡러 수익창출 방법 직장인 부업 초보자',
            'type': 'Evergreen Guide'
        }
    ]
    
    results = []
    
    for i, topic in enumerate(topics, 1):
        log(f"\n{'='*60}")
        log(f"[TOPIC {i}/3] {topic['name']} ({topic['type']})")
        log(f"{'='*60}")
        
        # 1. 노트북 생성
        log("[1/5] Creating notebook...")
        try:
            nb = client.create_notebook(topic['name'][:40])
            notebook_id = getattr(nb, 'id', None) or getattr(nb, 'notebook_id', None) or str(nb)
            log(f"  Notebook ID: {notebook_id}")
        except Exception as e:
            log(f"  ERROR: {e}")
            continue
        
        # 2. Deep Research 시작
        log(f"[2/5] Starting deep research...")
        log(f"  Query: {topic['query'][:60]}...")
        try:
            research = client.start_research(
                notebook_id=notebook_id,
                query=topic['query'],
                mode='deep'
            )
            task_id = research.get('task_id') if isinstance(research, dict) else None
            log(f"  Task ID: {task_id}")
        except Exception as e:
            log(f"  ERROR: {e}")
            continue
        
        # 3. 완료 대기 (최대 8분)
        log("[3/5] Polling research status...")
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
            log("  TIMEOUT - skipping")
            continue
        
        # 4. 소스 임포트
        log("[4/5] Importing sources...")
        if sources and task_id:
            try:
                client.import_research_sources(notebook_id, task_id, sources)
                log(f"  Imported {len(sources)} sources")
            except Exception as e:
                log(f"  ERROR: {e}")
        
        # 5. 한국어 블로그 생성
        log("[5/5] Generating Korean blog...")
        try:
            blog = client.create_report(
                notebook_id=notebook_id,
                report_format="Blog Post",
                language="ko"
            )
            artifact_id = blog.get('artifact_id') if isinstance(blog, dict) else None
            log(f"  Artifact ID: {artifact_id}")
            
            # 다운로드 대기
            output_file = f"{topic['name'][:30]}_blog.md"
            log(f"  Waiting for generation...")
            time.sleep(60)
            
            for attempt in range(15):
                try:
                    client.download_report(notebook_id, output_file, artifact_id)
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content_len = len(f.read())
                    log(f"  DOWNLOADED: {output_file} ({content_len} chars)")
                    results.append({
                        'name': topic['name'], 
                        'file': output_file, 
                        'chars': content_len,
                        'sources': len(sources) if sources else 0,
                        'type': topic['type']
                    })
                    break
                except Exception as e:
                    log(f"  Attempt {attempt+1}: {e}")
                    time.sleep(20)
            
        except Exception as e:
            log(f"  ERROR: {e}")
    
    # 요약
    log(f"\n{'='*70}")
    log("SEO BLOG GENERATION COMPLETE")
    log(f"{'='*70}")
    for r in results:
        log(f"  [OK] {r['type']}: {r['file']}")
        log(f"       Sources: {r['sources']}, Chars: {r['chars']}")
    log(f"\nTotal: {len(results)}/3 blogs generated")
    
except Exception as e:
    log(f"FATAL ERROR: {e}")
    import traceback
    log(traceback.format_exc())

log_file.close()
print("Done! Check seo_blog_log.txt")
