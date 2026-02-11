import urllib.request

urls = [
    "https://trends.google.com/trends/trendingsearches/daily/rss?geo=KR",
    "https://trends.google.co.kr/trends/trendingsearches/daily/rss?geo=KR",
    "https://trends.google.com/trends/hottrends/atom/feed?pn=p23",
    "https://trends.google.com/trends/trendingsearches/realtime/rss?geo=KR&category=all"
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

for url in urls:
    print(f"Testing: {url}")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            print(f"✅ Success! Code: {response.getcode()}")
            print(f"Content preview: {response.read(100)}")
            break # Found one
    except Exception as e:
        print(f"❌ Failed: {e}")
