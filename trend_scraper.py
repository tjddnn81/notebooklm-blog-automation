import urllib.request
import xml.etree.ElementTree as ET
import datetime
import os

def fetch_google_trends_kr():
    """구글 트렌드 RSS(한국)를 파싱하여 실시간 급상승 검색어 Top 5를 가져옵니다."""
    url = 'https://trends.google.co.kr/trending/rss?geo=KR'
    # 봇 차단을 막기 위해 User-Agent 설정
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
        
        root = ET.fromstring(xml_data)
        channel = root.find('channel')
        
        trends = []
        # 상위 5개 트렌드만 추출
        for item in channel.findall('item')[:5]:
            title = item.find('title').text
            
            # 예상 검색량 (ht 네임스페이스)
            traffic_node = item.find('{https://trends.google.com/trends/trendingsearches/daily}approx_traffic')
            traffic = traffic_node.text if traffic_node is not None else "알 수 없음"
            
            # 관련 뉴스 아이템 추출
            news_items = []
            for news in item.findall('{https://trends.google.com/trends/trendingsearches/daily}news_item'):
                news_title_node = news.find('{https://trends.google.com/trends/trendingsearches/daily}news_item_title')
                news_snippet_node = news.find('{https://trends.google.com/trends/trendingsearches/daily}news_item_snippet')
                
                news_title = news_title_node.text if news_title_node is not None else ""
                news_snippet = news_snippet_node.text if news_snippet_node is not None else ""
                
                # HTML 태그 제거 및 정리
                news_title = news_title.replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
                news_snippet = news_snippet.replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
                
                if news_title:
                    news_items.append(f"- 제목: {news_title}\n  내용: {news_snippet}")
            
            trends.append({
                'title': title,
                'traffic': traffic,
                'news': news_items
            })
        return trends
    except Exception as e:
        print(f"트렌드 로드 중 에러 발생: {e}")
        return None

def generate_source_file(trends, filename='source_trend_auto.txt'):
    """추출한 트렌드를 NotebookLM이 소화하기 좋은 텍스트 소스 형태로 저장합니다."""
    if not trends:
        print("작성할 트렌드 데이터가 없습니다.")
        return False
        
    now = datetime.datetime.now()
    date_str = now.strftime("%Y년 %m월 %d일 %H시")
    
    # 텍스트 파일(재료) 생성
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# 🚀 자동 수집 리포트: 오늘({date_str})의 대한민국 실시간 급상승 트렌드 & 이슈\n\n")
        f.write("해당 문서는 구글 트렌드 빅데이터를 기반으로 실시간 크롤링된 대한민국의 핵심 이슈 리포트입니다. \n")
        f.write("이 재료를 활용하여 대중의 관심이 집중된 SEO 맞춤형 트래픽 블로그 포스트를 작성할 수 있습니다.\n\n")
        f.write("---\n\n")
        
        for i, trend in enumerate(trends, 1):
            f.write(f"## 🔥 {i}위 키워드: {trend['title']}\n")
            f.write(f"* **일일 예상 검색량:** {trend['traffic']}\n\n")
            
            if trend['news']:
                f.write("**📰 관련 핵심 언론 보도 내용:**\n")
                for news in trend['news']:
                    f.write(f"{news}\n\n")
            f.write("---\n\n")
            
    print(f"[Phase 2 자동화 성공] 데이터 스크래핑 완료! '{filename}' 파일이 생성되었습니다.")
    return True

if __name__ == "__main__":
    print("[시작] 구글 트렌드 RSS 크롤러 가동 시작...")
    trends_data = fetch_google_trends_kr()
    
    if trends_data:
        generate_source_file(trends_data)
