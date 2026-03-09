import os
import sys
import time
from notebooklm_tools.core.client import NotebookLMClient

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

BLOGS = [
    {
        "topic": "'환율 변동성과 인플레이션 헷징' 2026년 금(Gold) 및 비트코인 등 대체자산 포트폴리오 편입 이유",
        "source": "source_night_3_gold_crypto.txt",
        "output": "Night_Blog_3_CryptoGold.md"
    },
    {
        "topic": "'금리 인하의 최대 수혜주?' 2026년 글로벌 상업용 부동산 리츠(REITs) 위기 속 기회 잡기",
        "source": "source_night_4_reits.txt",
        "output": "Night_Blog_4_REITs.md"
    },
]

def generate_blog(client, blog_info):
    topic = blog_info['topic']
    source_file = blog_info['source']
    output_filename = blog_info['output']
    
    log("======================================================================")
    log(f"블로그 생성 시작 (야간 자동화): {topic}")
    log(f"소스: {source_file} -> 출력: {output_filename}")
    log("======================================================================")
    
    try:
        log("[1/6] Creating notebook...")
        notebook = client.create_notebook(topic)
        notebook_id = getattr(notebook, 'id', None) or getattr(notebook, 'notebook_id', None) or str(notebook)
        if hasattr(notebook, 'notebook_id'):
            notebook_id = notebook.notebook_id
        if not notebook_id:
            raise ValueError(f"Failed to get notebook ID from response: {notebook}")
        log(f"  Notebook ID: {notebook_id}")
        
        log(f"\n[2/6] Adding File source: {source_file}...")
        try:
            full_path = os.path.abspath(source_file)
            client.add_file(notebook_id, full_path)
            log(f"  [OK] {full_path}")
        except Exception as e:
            log(f"  [ERROR] File upload failed: {e}")
            return False
            
        log("  Waiting for source processing (10s)...")
        time.sleep(10)
        
        log("\n[3/6] Starting deep research...")
        deep_search_query = f"""
        당신은 상위 0.1%의 경제/금융/테크 분야 전문 인사이트 블로거입니다. 
        블로그 이름은 'Stay Log'이며, "혼돈의 시장에서 흔들리지 않는 투자의 기준을 제시합니다. 2026년 경제 전망과 미래 기술 트렌드를 심층 분석하는 전문 인사이트 채널"이라는 확고한 정체성을 가지고 있습니다.
        
        업로드된 분석 소스 문서({source_file})의 내용을 완벽하게 흡수하여, 구글 애드센스 SEO에 최적화된, 깊이 있고 통찰력 넘치는 에버그린(Evergreen) 블로그 포스트를 작성하세요.
        
        주제: {topic}
        
        [필수 작성 규칙]
        1. 첫 문단(서론): 독자의 불안감이나 호기심을 자극하고, 이 글을 읽음으로써 얻을 수 있는 명확한 '투자적 통찰'이나 '경제적 이득'을 예고할 것.
        2. 본론 전개: 제공된 소스의 내용을 단순 나열하지 마십시오. 전문가("Stay Log 에디터")의 시선에서 데이터를 해석하고, '왜 이런 현상이 일어나는가', '어떻게 대비해야 하는가'에 대한 깊이 있는 분석을 추가할 것.
        3. 신뢰감과 체류 시간 상승: 소제목(H2, H3), 번호 매기기, 볼드체를 적극 활용하여 정갈하고 가독성 높은 레이아웃을 구성할 것. 중간에 "💡 Stay Log's Insight" 와 같은 팁 블록을 넣어 전문성을 강조할 것.
        4. 결론: 단순한 요약이 아닌, 독자가 당장 투자나 실생활에 적용할 수 있는 강력한 '행동 지침(Action Plan)'과 장기적인 시각을 제시하며 웅장하게 마무리할 것.
        
        문체는 정중하면서도 확신에 찬 전문가의 어투(~합니다, ~입니다)를 사용하세요.
        형식은 완벽한 Markdown으로 출력해야 합니다.
        """
        try:
            client.start_research(notebook_id, deep_search_query, mode='deep')
        except Exception as e:
            log(f"  [WARNING] start_research returned: {e}. Will attempt to poll anyway.")
        
        log("\n[4/6] Polling research status...")
        start_time = time.time()
        timeout = 1200 # increased timeout for overnight run
        
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
                print(f"\n  [ERROR] Polling failed: {e}")
                time.sleep(10)
        
        log("\n[5/6] Generating blog post...")
        blog = client.create_report(
            notebook_id=notebook_id,
            report_format="Blog Post",
            language="ko"
        )
        
        artifact_id = blog.get('artifact_id') if isinstance(blog, dict) else getattr(blog, 'artifact_id', None)
            
        if not artifact_id:
            log(f"[FATAL ERROR] Could not extract artifact_id")
            return False
            
        log(f"  Artifact ID: {artifact_id}")
        log("  Waiting for generation (30s)...")
        time.sleep(30)
        
        log("[6/6] Downloading blog post...")
        report_content = None
        for attempt in range(15):
            try:
                client.download_report(notebook_id, output_filename, artifact_id)
                if os.path.exists(output_filename):
                    with open(output_filename, 'r', encoding='utf-8') as f:
                        report_content = f.read()
                    if len(report_content) > 100:
                        break
                else:
                    log(f"  Attempt {attempt+1}: file not created yet")
            except Exception as e:
                log(f"  Attempt {attempt+1}: report not ready {e}")
                time.sleep(15)
        
        if not report_content:
            log(f"[FATAL ERROR] Could not get report content for {topic}")
            return False
            
        log("\n======================================================================")
        log(f"SUCCESS! {topic}")
        log("======================================================================")
        log(f"  File: {output_filename}")
        log(f"  Size: {len(report_content)} characters")
        return True
        
    except Exception as e:
        log(f"[FATAL ERROR] {e}")
        return False

from notebooklm_tools.core.auth import load_cached_tokens

def main():
    try:
        tokens = load_cached_tokens()
        client = NotebookLMClient(cookies=tokens.cookies)
        log("[OK] Client initialized\n")
    except Exception as e:
        log(f"[ERROR] Failed to init client: {e}")
        return
        
    for idx, blog in enumerate(BLOGS):
        log(f"--- Processing {idx+1}/{len(BLOGS)} ---")
        generate_blog(client, blog)
        time.sleep(2)  # small buffer

if __name__ == "__main__":
    main()
