import os
import sys
import time
from notebooklm_tools.core.client import NotebookLMClient

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

BLOGS = [
    {
        "topic": "2026 벚꽃 개화시기 총정리 & 한국인 99%가 모르는 '인생샷 보장' 숨은 벚꽃 명소 BEST 5",
        "source": "source_1_cherry_blossom.txt",
        "output": "Spring_Trend_1_CherryBlossom.md"
    },
    {
        "topic": "겨울 코트 벗기 전 필수! 한 달 만에 5kg 빼는 '2026년형 뇌과학 기반 급찐급빠' 현실 루틴",
        "source": "source_2_diet.txt",
        "output": "Spring_Trend_2_Diet.md"
    },
    {
        "topic": "봄맞이 인테리어? 버리기만 해도 돈이 됩니다! 당근마켓 수익과 10만 원으로 호텔 로비 만드는 홈스타일링",
        "source": "source_3_interior_carrot.txt",
        "output": "Spring_Trend_3_Interior.md"
    },
    {
        "topic": "새학기&상반기 이직 시즌 필수: 2026년 가장 몸값 높은 'AI 노비서' 단숨에 길들이는 직장인/학생 필살기",
        "source": "source_4_ai_gemini.txt",
        "output": "Spring_Trend_4_AIGemini.md"
    },
]

def generate_blog(client, blog_info):
    topic = blog_info['topic']
    source_file = blog_info['source']
    output_filename = blog_info['output']
    
    log("======================================================================")
    log(f"블로그 생성 시작: {topic}")
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
        당신은 상위 0.1%의 수익형 블로그 전문 카피라이터입니다. 
        업로드된 트렌드 소스 문서({source_file})의 내용을 바탕으로 독자의 시선을 사로잡는 폭발적인 블로그 포스트를 작성하세요.
        
        주제: {topic}
        
        [필수 작성 규칙]
        1. 첫 문단은 독자의 '고통(Pain Point)'이나 '호기심'을 극대화하는 강력한 훅(Hook)으로 시작할 것.
        2. 제공된 파일의 내용을 단순 요약하지 말고, 독자가 당장 실천할 수 있는 현실적이고 구체적인 '행동 지침(Action Plan)'으로 재가공할 것.
        3. 소제목(H2, H3), 글머리 기호, 볼드체를 적극 활용하여 가독성을 극대화할 것.
        4. 중간중간 공감대 형성과 기대감을 높이는 문장을 배치할 것.
        5. 마지막에는 독자가 정보를 얻는 데 그치지 않고 즉각 행동하게 만드는 강력한 결론으로 마무리할 것.
        
        형식은 완벽한 Markdown으로 출력해야 합니다.
        """
        client.start_research(notebook_id, deep_search_query, mode='deep')
        
        log("\n[4/6] Polling research status...")
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
