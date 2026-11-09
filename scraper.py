import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
from datetime import datetime
import pytz

# 대표님이 지정한 타겟 언론사 리스트 (띄어쓰기 등 변수 대비)
TARGET_NATIONAL = ["조선일보", "중앙일보", "동아일보", "한겨레", "경향신문", "한국일보", "서울신문", "문화일보", "세계일보", "국민일보"]
TARGET_JEJU = ["제주의소리", "헤드라인제주", "한라일보", "제민일보", "제주매일", "JIBS"]

def categorize_source(source_name):
    """언론사 이름을 보고 그룹과 우선순위를 정해줍니다."""
    # 제주 언론인지 확인
    if any(jeju in source_name for jeju in TARGET_JEJU):
        return "제주 언론", 1
    # 중앙지인지 확인
    elif any(national in source_name for national in TARGET_NATIONAL):
        return "중앙지", 2
    # 그 외
    else:
        return "기타", 3

def fetch_news():
    # 1. 전문 키워드 대폭 확장 (OR 조건으로 묶음)
    keywords = "기후 OR 에너지 OR 전력시장 OR 전력계통 OR 탄소시장 OR 탄소크레딧 OR 해상풍력 OR 태양광"
    search_query = urllib.parse.quote(f"{keywords} when:1d")
    
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
        
        # 언론사 그룹과 우선순위 판별
        group, priority = categorize_source(source)
        
        news_list.append({
            "title": clean_title,
            "link": link,
            "source": source,
            "group": group,
            "priority": priority,
            "date": pubDate
        })
    
    # 2. 우선순위(priority)를 기준으로 기사 정렬 (1:제주 -> 2:중앙 -> 3:기타 순서)
    news_list.sort(key=lambda x: x['priority'])
    
    # 3. 날짜 및 시간 세팅
    korea_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(korea_tz)
    today_date_str = now.strftime("%m월 %d일")
    update_time_str = now.strftime("%m월 %d일 오전 08:00")
    
    result = {
        "today_date": today_date_str,
        "update_time": update_time_str,
        "articles": news_list
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    fetch_news()
