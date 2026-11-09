import urllib.request
import urllib.parse  # 한글 검색어를 변환해주는 부품 추가
import xml.etree.ElementTree as ET
import json
from datetime import datetime
import pytz

def fetch_news():
    # 1. '기후 OR 에너지'라는 한글 검색어를 컴퓨터가 읽을 수 있게 변환(인코딩)합니다.
    search_query = urllib.parse.quote("기후 OR 에너지 when:1d")
    
    # 2. 변환된 검색어를 주소에 쏙 넣습니다.
    url = f"https://news.google.com/rss/search?q={search_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
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
        
        news_list.append({
            "title": clean_title,
            "link": link,
            "source": source,
            "date": pubDate
        })
    
    korea_tz = pytz.timezone('Asia/Seoul')
    update_time = datetime.now(korea_tz).strftime("%m월 %d일 오전 08:00")
    
    result = {
        "update_time": update_time,
        "articles": news_list
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    fetch_news()
