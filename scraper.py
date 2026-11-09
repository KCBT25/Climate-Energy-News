import urllib.request
import xml.etree.ElementTree as ET
import json
from datetime import datetime, timedelta
import pytz

def fetch_news():
    # 구글 뉴스 RSS URL (기후 OR 에너지, 한국어, 최근 1일)
    url = "https://news.google.com/rss/search?q=기후+OR+에너지+when:1d&hl=ko&gl=KR&ceid=KR:ko"
    
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
        
        # 제목에서 언론사 이름이 중복 표기되는 것 방지
        clean_title = title.rsplit(' - ', 1)[0]
        
        news_list.append({
            "title": clean_title,
            "link": link,
            "source": source,
            "date": pubDate
        })
    
    # 한국 시간 기준으로 업데이트 시간 기록
    korea_tz = pytz.timezone('Asia/Seoul')
    update_time = datetime.now(korea_tz).strftime("%m월 %d일 오전 08:00")
    
    result = {
        "update_time": update_time,
        "articles": news_list
    }
    
    # JSON 파일로 저장 (프론트엔드에서 이 파일을 읽어감)
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    fetch_news()
