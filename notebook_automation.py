import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import argparse

# NotebookLM Tools
try:
    from notebooklm_tools.core.client import NotebookLMClient
    from notebooklm_tools.core.auth import load_cached_tokens
except ImportError:
    print("Error: notebooklm-mcp-cli package not found. Please install it via pip.")
    sys.exit(1)

def get_google_trends_kr(count=5):
    """Fetches top trending keywords from Google Trends Korea RSS."""
    # Updated URL to .com
    urls = [
        "https://trends.google.co.kr/trends/trendingsearches/daily/rss?geo=KR",
        "https://trends.google.com/trends/trendingsearches/daily/rss?geo=KR",
        # Realtime search trends (if daily fails)
        "https://trends.google.com/trends/hottrends/atom/feed?pn=p23" 
    ]
    
    for rss_url in urls:
        print(f"📉 Fetching Google Trends from: {rss_url}")
        try:
            req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
            with urllib.request.urlopen(req) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                
                # Different feeds have different structures
                items = root.findall(".//item")
                if not items:
                     # Atom feed structure?
                     items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
                
                trends = []
                for item in items[:count]:
                    # RSS vs Atom
                    title_node = item.find("title")
                    if title_node is None:
                        title_node = item.find("{http://www.w3.org/2005/Atom}title")
                        
                    if title_node is not None:
                        trends.append(title_node.text)
                
                if trends:
                    return trends
                    
        except Exception as e:
            print(f"❌ Failed to fetch trends from {rss_url}: {e}")
            continue
            
    return []

def authenticate():
    """Loads cached tokens and initializes the client."""
    print("🔐 Authenticating...")
    try:
        tokens = load_cached_tokens()
        # Handle different token structures
        if hasattr(tokens, 'cookies'):
            cookies = tokens.cookies
        elif isinstance(tokens, dict) and 'cookies' in tokens:
            cookies = tokens['cookies']
        else:
            # Fallback attempts
            cookies = getattr(tokens, 'cookie_jar', None) or getattr(tokens, 'token', None)
        
        if not cookies:
            raise ValueError("Could not extract cookies from tokens.")
            
        client = NotebookLMClient(cookies=cookies)
        return client
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("Please run 'nlm login' in your terminal first.")
        sys.exit(1)

def run_research_and_write(client, topic):
    """Orchestrates the research and writing process for a single topic."""
    logger_header = f"[{topic}]"
    print(f"\n🚀 {logger_header} Starting automation sequence...")
    
    # 1. Create Notebook
    # Note: notebooklm_tools might not return the ID directly from create_notebook depending on version.
    # Let's check listing after creation or check return value.
    # 1. Get or Create Notebook
    notebook_id = None
    existing_source_count = 0
    
    try:
        print(f"{logger_header} Checking for existing notebook...")
        notebooks = client.list_notebooks()
        existing_nb = next((nb for nb in notebooks if nb.title.startswith(topic)), None)
        
        if existing_nb:
            print(f"{logger_header} Found existing notebook: {existing_nb.title} ({existing_nb.id})")
            notebook_id = existing_nb.id
            existing_source_count = existing_nb.source_count
            print(f"{logger_header} Existing source count: {existing_source_count}")
        else:
            print(f"{logger_header} Creating notebook...")
            title = f"{topic}_{datetime.now().strftime('%Y%m%d_%H%M')}"
            nb = client.create_notebook(title)
            
            # Extract ID logic
            if isinstance(nb, dict):
                notebook_id = nb.get('id') or nb.get('notebookId')
            else:
                 notebook_id = getattr(nb, 'id', None) or getattr(nb, 'notebookId', None)
                 
            # Fallback ID extraction
            if not notebook_id:
                 time.sleep(2)
                 notebooks = client.list_notebooks()
                 for nb_item in notebooks:
                     nb_title = nb_item.title if hasattr(nb_item, 'title') else nb_item.get('title')
                     if nb_title == title:
                         notebook_id = nb_item.id if hasattr(nb_item, 'id') else nb_item.get('id')
                         break
            
            print(f"{logger_header} Notebook created! ID: {notebook_id}")
            
    except Exception as e:
        print(f"❌ {logger_header} Failed to create/find notebook: {e}")
        return

    # 2. Start Deep Research (if needed)
    if existing_source_count >= 5:
        print(f"{logger_header} Notebook already has meaningful content. Skipping research.")
    else:
        try:
            print(f"{logger_header} Initiating Deep Research (Mode: DEEP) via CLI...")
            # Use CLI command via subprocess for reliability
            import subprocess
            # Absolute path to nlm.exe found via dir command
            nlm_path = r"C:\Users\tjddn\AppData\Local\Python\pythoncore-3.14-64\Scripts\nlm.exe"
            # CORRECT CLI SYNTAX: nlm research start "QUERY" -n NOTEBOOK_ID -m deep
            # (--topic doesn't exist, it's a positional argument!)
            cmd = [nlm_path, "research", "start", topic, "-n", notebook_id, "-m", "deep"]
            
            # Fix: Do NOT use text=True/encoding='utf-8' here to prevent UnicodeDecodeError on Windows CP949
            result = subprocess.run(cmd, capture_output=True, shell=True)
            
            # Manual decoding with fallback
            def safe_decode(bytes_data):
                try:
                    return bytes_data.decode('utf-8')
                except UnicodeDecodeError:
                    return bytes_data.decode('cp949', errors='replace')
            
            stdout_str = safe_decode(result.stdout)
            stderr_str = safe_decode(result.stderr)
            
            if result.returncode != 0:
                 print(f"❌ {logger_header} CLI Research failed: {stderr_str}")
                 # Don't return yet, maybe poll finds something? No, failed.
            else:
                print(f"{logger_header} Research command sent. Output: {stdout_str.strip()[:100]}...")
                print(f"{logger_header} Waiting for sources to populate...")
            
            # 3. Poll for completion (Hybrid/List approach)
            max_retries = 60 # 10 mins
            research_complete = False
            
            for i in range(max_retries):
                time.sleep(10)
                
                try:
                    notebooks = client.list_notebooks()
                    target_nb = next((nb for nb in notebooks if nb.id == notebook_id), None)
                    if target_nb:
                        source_count = target_nb.source_count
                        print(f"{logger_header} ... Sources: {source_count} (Time: {i*10}s)")
                        
                        if source_count >= 5:
                             print(f"{logger_header} Sufficient sources found ({source_count})!")
                             research_complete = True
                             break
                except Exception as poll_err:
                    print(f"Poll check failed: {poll_err}")
            
            if not research_complete:
                print(f"⚠️ {logger_header} Research timed out or insufficient sources (<5). Aborting generation.")
                return # STRICT EXIT

        except Exception as e:
            print(f"❌ {logger_header} Research process failed: {e}")
            return

    # 4. Generate Blog Post (Monetization Optimized)
    try:
        print(f"{logger_header} Generating Profit-Optimized Blog Post...")
        
        # High-Yield SEO Prompt
        prompt = f"""
        당신은 월 1000만원 수익을 내는 프로 블로그 에디터입니다.
        주제: '{topic}'
        
        아래 지침에 따라 독자를 사로잡는 '수익화 최적화' 블로그 포스팅을 작성해 주세요.
        
        [필수 요구사항]
        1. **제목**: 클릭을 유도하는 매력적이고 자극적인 제목 3가지를 먼저 제안하세요. (예: ~하는 5가지 이유, 충격적인 진실 등)
        2. **서론 (Hook)**: 독자가 이 글을 읽지 않으면 손해라고 느낄 만큼 강력한 후킹으로 시작하세요.
        3. **본론 (Value)**: 수집된 소스(Source)를 바탕으로, 단순 정보 나열이 아닌 '인사이트'와 '구체적인 분석'을 제공하세요. 가독성을 위해 소제목과 글머리 기호를 적극 활용하세요.
        4. **결론 (Action)**: 독자의 기억에 남는 강렬한 마무리 멘트를 작성하세요.
        5. **SEO 키워드**: 글 중간중간에 검색량이 많은 관련 키워드를 자연스럽게 녹여내세요.
        
        언어: 한국어 (매끄럽고 전문적인, 그러나 읽기 쉬운 어조)
        형식: 마크다운 (Markdown)
        """
        
        result = client.query(notebook_id, prompt)
        
        # Extract text
        content = ""
        if isinstance(result, dict):
            content = result.get('answer') or result.get('text') or str(result)
        else:
            content = getattr(result, 'answer', None) or getattr(result, 'text', None) or str(result)
            
        # Save to file
        filename = f"Report_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Report: {topic}\n\n")
            f.write(content)
            
        print(f"✅ {logger_header} Success! Report saved to: {filename}")
        
    except Exception as e:
        print(f"❌ {logger_header} Generation failed: {e}")

    # 5. Generate Studio Assets (Audio, FAQ, Briefing)
    try:
        print(f"{logger_header} Generating Premium Studio Assets...")
        
        # Audio Overview
        print(f"{logger_header} requesting Audio Overview...")
        try:
             # Using defaults: format_code=1 (Summary?), length_code=2 (Medium?), language='ko'? 
             # Signature was: (notebook_id, source_ids=None, format_code=1, length_code=2, language='en', focus_prompt='')
             # Let's try language='ko' if supported, otherwise 'en'. NotebookLM audio is usually native English but let's see.
             # Actually, for Korean content, it might speak English about it unless we set language key if API supports it.
             # Inspection showed 'language' arg default 'en'. I will try 'ko'.
             client.create_audio_overview(notebook_id, language='ko')
             print(f"🔊 {logger_header} Audio Overview generation started!")
        except Exception as e:
             print(f"⚠️ {logger_header} Audio generation skipped: {e}")

        # Briefing Doc (as Study Guide/FAQ alternative)
        print(f"{logger_header} requesting Briefing Doc...")
        try:
             # create_report(notebook_id, custom_prompt='', report_format='Briefing Doc', language='en')
             # Let's try to make an FAQ using custom prompt in create_report or just Briefing Doc
             client.create_report(notebook_id, report_format='Briefing Doc', language='ko')
             print(f"📄 {logger_header} Briefing Doc created!")
             
             # FAQ
             client.create_report(notebook_id, report_format='FAQ', custom_prompt='Create a detailed FAQ for this topic.', language='ko')
             print(f"❓ {logger_header} FAQ created!")
             
        except Exception as e:
             print(f"⚠️ {logger_header} Report generation skipped: {e}")
             
        print(f"✨ {logger_header} All Studio assets requested. Check NotebookLM Web UI!")
        
    except Exception as e:
        print(f"❌ {logger_header} Studio generation failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="NotebookLM Master Automation")
    parser.add_argument("--mode", choices=["topic", "trends"], default="topic", help="Mode: single topic or trends loop")
    parser.add_argument("--topic", type=str, help="Topic for single mode")
    parser.add_argument("--count", type=int, default=5, help="Number of trends to process")
    
    args = parser.parse_args()
    
    client = authenticate()
    
    if args.mode == "trends":
        print(f"📊 Starting Trends Mode (Count: {args.count})")
        trends = get_google_trends_kr(args.count)
        if not trends:
            print("No trends found.")
            return
            
        print(f"Found Trends: {trends}")
        for idx, topic in enumerate(trends):
            print(f"\n--- Processing Trend {idx+1}/{len(trends)}: {topic} ---")
            run_research_and_write(client, topic)
            
    elif args.mode == "topic":
        if not args.topic:
            # Interactive mode if argument missing
            topic = input("Enter a topic to research: ")
        else:
            topic = args.topic
        
        run_research_and_write(client, topic)

if __name__ == "__main__":
    main()
