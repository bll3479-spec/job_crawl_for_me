import requests
from bs4 import BeautifulSoup

url = "https://www.saramin.co.kr/zf_user/search/recruit?searchword=데이터분석&loc_mcd=101000&exp_cd=1&recruitPageCount=40"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")

items = soup.select("div.item_recruit")     #공고 블록 40개, 리스트
first = items[0]                            #첫번째 공고 블록  
# 1 단계: 첫번째 공고만 뽑아보기
# title = first.select_one("h2.job_tit a")    #블록 내에서 제목 링크 하나 찾기
# print(title.get_text(strip=True))
# print(title["href"])

#2단계: 40개 전부를 반복 처리하여 딕셔너리 리스트로 바꾸기
from urllib.parse import urljoin
jobs = []               #공고 하나당 딕셔너리가 들어감
for item in items:
    title = item.select_one("h2.job_tit a")     #공고 블록 40개를 하나씩 꺼냄
    if title is None:
        continue
    company_tag = item.select_one("strong.corp_name a")     #회사명 태그
    company = company_tag.get_text(strip=True) if company_tag else ""
    cond_tags = item.select("div.job_condition span")  #근무조건 태그들 리스트로.
    conditions = " / ".join(c.get_text(strip=True) for c in cond_tags)  #리스트에서 글자만 꺼내 " / "로 이어붙임.
    deadline_tag = item.select_one("div.job_date span.date")    #마감일 태그
    deadline = deadline_tag.get_text(strip=True) if deadline_tag else ""
    
    jobs.append({
        "title" : title.get_text(strip=True),
        "company" : company,            #딕셔너리에 칸 추가
        "link" : urljoin("https://www.saramin.co.kr", title["href"]),
        "conditions" : conditions,
        "deadline" : deadline
    })

print(len(jobs), "건")
print(jobs[0])
print(jobs[-1])