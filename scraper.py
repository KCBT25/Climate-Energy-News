import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
from datetime import datetime
import pytz

TARGET_MAIN = ["조선일보", "중앙일보", "동아일보", "한겨레", "경향신문", "한국일보", "서울신문", "문화일보", "세계일보", "국민일보"]
TARGET_JEJU = ["제주의소리", "헤드라인제주", "한라일보", "제민일보", "제주매일", "JIBS"]

def categorize_source(source_name):
    if any(jeju in source_name for jeju in TARGET_JEJU):
        return "제주 언론", 1
    elif any(national in source_name for national in TARGET_MAIN):
        return "주요언론사", 2
    else:
        return "기타", 3

def fetch_news():
    keywords = "기후 OR 에너지 OR 전력시장 OR 전력계통 OR 탄소시장 OR 탄소크레딧 OR 해상풍력 OR 태양광 OR RE100 OR 송전망"
    search_query = urllib.parse.quote(f"{keywords} when:1d")
    url = f"https://news.google.com/rss/search?q={search_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    # [핵심 수정] 구글 차단을 피하기 위해 윈도우 PC의 크롬 브라우저인 것처럼 신분을 위장합니다.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    xml_data = response.read()
    
    root = ET.fromstring(xml_data)
    news_list = []
    
    for item in root.findall('./channel/item'):
        title = item.find('title').text
        link = item.find('link').text
        pubDate = item.find('pubDate').text
        source = item.find('source').text if item.find('source') is not None else "기타 언론사"
        
        clean_title = title.rsplit(' - ', 1)[0]
        group, priority = categorize_source(source)
        
        news_list.append({
            "title": clean_title,
            "link": link,
            "source": source,
            "group": group,
            "priority": priority,
            "date": pubDate
        })
    
    news_list.sort(key=lambda x: x['priority'])
    
    korea_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(korea_tz)
    
    result = {
        "today_date": now.strftime("%m월 %d일"),
        "update_time": now.strftime("%m월 %d일 오전 08:00"),
        "articles": news_list
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    fetch_news()
