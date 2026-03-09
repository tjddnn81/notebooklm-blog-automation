import os
import sys
import time
import datetime
import urllib.request
import xml.etree.ElementTree as ET
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# =========== [Phase 1: 트렌드 자동 스크래핑 로직] ===========
def fetch_google_trends_kr():
    url = 'https://trends.google.co.kr/trending/rss?geo=KR'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        channel = root.find('channel')
        trends = []
        for item in channel.findall('item')[:5]:
            title = item.find('title').text
            traffic_node = item.find('{https://trends.google.com/trends/trendingsearches/daily}approx_traffic')
            traffic = traffic_node.text if traffic_node is not None else "알 수 없음"
            news_items = []
            for news in item.findall('{https://trends.google.com/trends/trendingsearches/daily}news_item'):
                news_title_node = news.find('{https://trends.google.com/trends/trendingsearches/daily}news_item_title')
                news_snippet_node = news.find('{https://trends.google.com/trends/trendingsearches/daily}news_item_snippet')
                news_title = news_title_node.text.replace('<b>', '').replace('</b>', '').replace('&quot;', '"') if news_title_node is not None else ""
                news_snippet = news_snippet_node.text.replace('<b>', '').replace('</b>', '').replace('&quot;', '"') if news_snippet_node is not None else ""
                if news_title:
                    news_items.append(f"- 제목: {news_title}\n  내용: {news_snippet}")
            trends.append({'title': title, 'traffic': traffic, 'news': news_items})
        return trends
    except Exception as e:
        print(f"트렌드 로드 중 에러 발생: {e}")
        return None

def generate_source_file(top_trend, filename='source_trend_auto.txt'):
    if not top_trend:
        return False
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# 🚀 핵심 리서치 소스\n\n")
        f.write("본 문서는 특정 주제에 대한 심층 분석용 텍스트베이스입니다.\n\n")
        f.write(f"## 주제: {top_trend['title']}\n\n")
        if top_trend['news']:
            for news in top_trend['news']:
                f.write(f"{news}\n\n")
    return True

# =========== [Phase 2: NotebookLM 블로그 생성 (Spicy 프롬프트)] ===========
from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def automate_blog_generation(top_keyword, source_file, output_filename):
    topic = f"'{top_keyword}'에 대한 심층 분석 및 비즈니스 인사이트"
    
    try:
        tokens = load_cached_tokens()
        client = NotebookLMClient(cookies=tokens.cookies)
        log("[OK] NotebookLM Client initialized")
    except Exception as e:
        log(f"[ERROR] Failed to init client: {e}")
        return

    log("======================================================================")
    log(f"[시작] 완전 무인 자동화 블로그 생성 시작")
    log(f"메인 타겟 키워드: {top_keyword}")
    log(f"소스: {source_file} -> 출력: {output_filename}")
    log("======================================================================")
    
    try:
        log("[1/6] Creating notebook...")
        notebook = client.create_notebook("DeepResearch: " + top_keyword)
        notebook_id = getattr(notebook, 'id', None) or getattr(notebook, 'notebook_id', None) or str(notebook)
        if hasattr(notebook, 'notebook_id'):
            notebook_id = notebook.notebook_id
        log(f"  Notebook ID: {notebook_id}")
        
        log(f"\n[2/6] Reading local transcript and adding Text source...")
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
        source_info = client.add_text_source(notebook_id, content, title=topic, wait=True, wait_timeout=300)
        
        log("\n[3/6] Starting deep research (극강의 에버그린 프롬프트 주입!)...")
        deep_search_query = f"""
        당신은 특정 주제에 대해 10년 넘게 연구해온 최고의 칼럼니스트입니다.
        이번 글의 유일한 목적은 시대를 전혀 타지 않는, 10년 뒤에 읽어도 가치 있는 완벽한 '에버그린(Evergreen) 칼럼'을 작성하는 것입니다.
        
        주제: '{top_keyword}' 자체에 대한 심층 분석 및 본질적 통찰
        
        [🚨 초강력 에버그린 작성 5계명 🚨] (이를 어기면 칼럼이 즉시 폐기됩니다)
        1. 시간/날짜/시의성 언급 절대 금지: "오늘", "어제", "올해", "요즘", "최근", "3월 8일", "2026년", "현재", "실시간", "트렌드", "검색어", "순위" 같은 단어는 단 한 개라도 절대 쓰면 안 됩니다. 이 글은 특정 날짜에 종속된 뉴스 보도가 아닙니다.
        2. 소스 파일(리포트) 요약 절대 금지: 제공된 텍스트는 당신 이미 알고 있는 지식입니다. "이 문서에 따르면", "차트를 보면" 같은 기계적인 리포트 말투를 100% 배제하세요.
        3. 본질에 집중한 딥서치: '{top_keyword}'라는 주제 그 자체의 역사적, 경제적, 사회적 본질에 대해서만 깊이 파고드세요. (예를 들어 '세계 여성의 날'이라면, 이 기념일이 가지는 사회적 질서의 변화나 거시적 가치관의 이동에만 집중하세요.)
        4. 뼈 때리는 사이다 구어체: 백과사전처럼 딱딱하게 쓰지 마세요. 독자에게 직접 말 거는 친근하고 확고한 구어체(~해요, ~죠, 솔직히 까놓고 말해서 등)를 사용하세요.
        5. 변하지 않는 인사이트: 이 현상의 변하지 않는 본질을 알면 독자의 삶이나 비즈니스에 어떤 장기적 도움이 되는지 명쾌한 결론을 내어주세요.
        
        절대 "뉴스 기사"나 "트렌드 리포트" 뉘앙스가 1%도 들어가면 안 됩니다. 완벽하게 시그니처 칼럼으로 작성하여, 완벽한 Markdown으로 출력하세요.
        """
        try:
            client.start_research(notebook_id, deep_search_query, mode='deep')
        except Exception as e:
            pass # ignore generic response errors when polling works
        
        log("\n[4/6] Polling research status...")
        start_time = time.time()
        while True:
            elapsed = int(time.time() - start_time)
            if elapsed > 1200:
                raise TimeoutError("Research timed out")
            try:
                poll = client.poll_research(notebook_id)
                if poll and isinstance(poll, dict):
                    state = poll.get('state') or poll.get('status')
                    if state in ('completed', 'done'):
                        print("")
                        log(f"  COMPLETED!")
                        break
                    elif state and 'fail' in str(state).lower():
                        raise Exception(f"Research failed: {state}")
                time.sleep(10)
            except Exception as e:
                time.sleep(10)
        
        log("\n[5/6] Generating blog post...")
        blog = client.create_report(notebook_id=notebook_id, report_format="Blog Post", language="ko")
        artifact_id = blog.get('artifact_id') if isinstance(blog, dict) else getattr(blog, 'artifact_id', None)
        time.sleep(30)
        
        log("[6/6] Downloading blog post...")
        report_content = None
        for attempt in range(15):
            try:
                client.download_report(notebook_id, output_filename, artifact_id)
                if os.path.exists(output_filename):
                    with open(output_filename, 'r', encoding='utf-8') as f:
                        if len(f.read()) > 100:
                            report_content = True
                            break
            except Exception:
                pass
            time.sleep(15)
            
        log("\n======================================================================")
        log("[성공] 로컬 무인 공장 가동 완료! 블로그 생성이 완료되었습니다!")
        log(f"저장된 파일: {output_filename}")
        log("======================================================================")
        
    except Exception as e:
        log(f"[FATAL ERROR] {e}")

if __name__ == "__main__":
    print("[시스템] 궁극의 로컬 무인 공장 파이프라인 가동을 시작합니다...")
    
    # 1. 트렌드 스크래핑
    trends = fetch_google_trends_kr()
    if not trends:
        print("[에러] 트렌드를 가져오지 못했습니다.")
        sys.exit(1)
        
    print("\n========================================================")
    print("🔥 현재 대한민국 실시간 급상승 트렌드 TOP 5 🔥")
    print("========================================================")
    for i, t in enumerate(trends, 1):
        print(f"[{i}] {t['title']} (검색량: {t['traffic']})")
    print("========================================================\n")
    
    try:
        user_input = input("✅ 블로그로 발행할 트렌드 번호를 선택하세요 (1~5) [취소: q]: ")
        if user_input.strip().lower() == 'q':
            print("작업을 취소합니다.")
            sys.exit(0)
            
        choice = int(user_input.strip())
        if choice < 1 or choice > 5:
            raise ValueError()
    except ValueError:
        print("[에러] 잘못된 입력입니다. 1에서 5 사이의 숫자를 입력하세요.")
        sys.exit(1)
        
    selected_trend = trends[choice - 1]
    top_keyword = selected_trend['title']
    print(f"\n=> [{choice}] '{top_keyword}' 트렌드로 블로그 생성을 시작합니다!\n")
    
    source_filename = "source_trend_auto.txt"
    generate_source_file(selected_trend, source_filename)
    
    # 2. 오늘 날짜 포맷으로 출력 파일명 생성 (파일명 길이 및 특수기호 안전 처리)
    import re
    safe_keyword = re.sub(r'[^\w\s-]', '', top_keyword).strip().replace(' ', '_')
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    output_filename = f"Trend_Blog_Auto_{date_str}_{safe_keyword}.md"
    
    # 3. NotebookLM 자동화 로직 호출
    automate_blog_generation(top_keyword, source_filename, output_filename)
