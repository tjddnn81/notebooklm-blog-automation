import os
import sys
import time
from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def main():
    # 블로그 설정
    topic = "2026 WBC 한국 17년 만의 8강, 예전 WBC와 달라진 야구의 돈: 중계권 전쟁부터 스포츠 경제학까지"
    source_file = "source_wbc_baseball_economics.txt"
    output_filename = "WBC_2026_야구경제학_블로그.md"

    try:
        tokens = load_cached_tokens()
        client = NotebookLMClient(cookies=tokens.cookies)
        log("[OK] Client initialized\n")
    except Exception as e:
        log(f"[ERROR] Failed to init client: {e}")
        return

    log("======================================================================")
    log(f"트렌드 블로그 생성 시작: {topic}")
    log(f"소스: {source_file} -> 출력: {output_filename}")
    log("======================================================================")

    try:
        # 1단계: 노트북 생성
        log("[1/6] Creating notebook...")
        notebook = client.create_notebook("WBC 야구 경제학")
        notebook_id = getattr(notebook, 'id', None) or getattr(notebook, 'notebook_id', None) or str(notebook)
        if hasattr(notebook, 'notebook_id'):
            notebook_id = notebook.notebook_id
        if not notebook_id:
            raise ValueError(f"Failed to get notebook ID from response: {notebook}")
        log(f"  Notebook ID: {notebook_id}")

        # 2단계: 소스 텍스트 추가
        log(f"\n[2/6] Reading local source and adding Text source: {source_file}...")
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            source_info = client.add_text_source(notebook_id, content, title=topic, wait=True, wait_timeout=300)

            if source_info and 'id' in source_info:
                log(f"  [OK] Added Text Source ID: {source_info['id']}")
            else:
                log(f"  [ERROR] Failed to get source info: {source_info}")
                return False

        except Exception as e:
            log(f"  [ERROR] Text source addition failed: {e}")
            return False

        # 3단계: Deep Research (도파민 프롬프트 주입)
        log("\n[3/6] Starting deep research (도파민 프롬프트 주입!)...")
        deep_search_query = f"""
        당신은 상위 0.1%의 경제/금융/테크 분야 전문 인사이트 블로거이자, 구독자들의 뼈를 때리는 '팩트폭행' 1타 강사입니다.
        블로그 이름은 'Stay Log'입니다.
        이번 글의 목적은 '노잼'이고 지루한 경제 글에 지친 독자들에게 '도파민'을 터뜨려주면서도 팩트와 인사이트를 뇌리에 꽂아넣는 것입니다.

        업로드된 텍스트 소스 문서({source_file})의 내용을 철저히 분석하고 요약하여 구글 애드센스 SEO에 최적화된 블로그 포스트를 작성하세요.

        주제: {topic}

        [🔥 핵심 앵글: "예전의 WBC와 현재의 WBC는 다르다"]
        - 2009년 준우승 시절 vs 2026년 17년 만의 8강 진출: 한국 야구 위상의 변화
        - 지상파 무료 중계 vs OTT 독점 중계: 스포츠 시청의 패러다임 시프트
        - 일본 Netflix 독점 논란 ($63.5M, 가입자 1000만 vs 기존 시청자 3900만)
        - 한국 CJ ENM 티빙 독점 + 보편적 시청권 하이브리드 모델
        - 상금 2.6배 폭등 ($1440만 → $3750만), 일본 우승 시 경제효과 8635억 원
        - "스포츠는 이제 보는 것이 아니라 소비하는 것이다" — 돈의 흐름 분석

        [🚨 유튜브형 초강력 도파민 작성 규칙 🚨]
        1. 멱살 잡는 서론 (Hooking): "2009년과 2026년, 같은 WBC인데 왜 완전히 다른 게임이 됐을까?" 같은 질문형 어그로로 시작.
        2. 뼈 때리는 팩트 폭행과 사이다 말투: 딱딱한 경제 잡지 말투를 버리고, '슈카월드' 채널 패널처럼 친근하고 확신에 찬 구어체(~해요, ~죠, 팩트를 말씀드릴게요 등)를 100% 사용하세요.
        3. 찰떡 비유 (스토리텔링): 어려운 경제/테크 용어는 일상적인 내용(연애, 게임, 노가다 등)으로 비유해서 쉽고 찰지게 설명하세요.
        4. 시각적 도파민 마사지: 단락마다 🚀, 🔥, 💡, 🚨, 💸, 🤑, 😅, ⚾, 📺 등의 이모지를 팍팍 넣어서 스크롤의 지루함을 박살 내세요.
        5. 기승전결과 명확한 핵심 전략: 재미만 있는 게 아니라, 결국 "그래서 투자자/소비자로서 어떻게 대응해야 하는데?"에 대한 명확한 인사이트를 콕 집어주면서 마무리하세요.
        6. 과거 vs 현재 비교 표를 반드시 포함하세요.

        형식은 완벽한 Markdown으로 출력해야 합니다. 독자가 잠에서 번쩍 깰 정도로 재밌고 흡입력 있게 작성하세요!
        """
        try:
            client.start_research(notebook_id, deep_search_query, mode='deep')
        except Exception as e:
            log(f"  [WARNING] start_research returned: {e}. Will attempt to poll anyway.")

        # 4단계: 리서치 완료 대기
        log("\n[4/6] Polling research status...")
        start_time = time.time()
        timeout = 1200

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

        # 5단계: 블로그 리포트 생성
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

        # 6단계: 다운로드
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
            log(f"[FATAL ERROR] Could not get report content")
            return False

        log("\n======================================================================")
        log(f"SUCCESS! {topic}")
        log("======================================================================")
        log(f"  File: {output_filename}")
        log(f"  Size: {len(report_content)} characters")

    except Exception as e:
        log(f"[FATAL ERROR] {e}")

if __name__ == "__main__":
    main()
