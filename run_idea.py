import datetime
from master_automation import automate_blog_generation

topic = "애국심은 어떻게 가장 확실한 돈이 되는가? (WBC 도파민 마케팅 수익률 분석)"
source_file = "source_trend_3_patriotism.txt"

# 파일명 안전하게 처리
import re
safe_keyword = re.sub(r'[^\w\s-]', '', topic).strip().replace(' ', '_')
date_str = datetime.datetime.now().strftime("%Y%m%d")
# 파일명이 너무 길어질 수 있으므로 짧게 지정
output_file = f"Trend_Blog_Auto_{date_str}_Patriotism_Marketing.md"

print(f"[{datetime.datetime.now()}] 블로그 생성 시작: {topic}")
automate_blog_generation(topic, source_file, output_file)
print(f"[{datetime.datetime.now()}] 블로그 생성 완료: {output_file}")
