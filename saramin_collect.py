import requests, time, re, csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import date

BASE = "https://www.saramin.co.kr/zf_user/search/recruit"
KEYWORDS = ["데이터분석", "데이터엔지니어", "데이터사이언티스트", "머신러닝", "인공지능", "AI", "AI 자동화", "챗봇", "RAG", "추천시스템", "AI 서비스 기획"]
PAGES = 2
LOC_CD = "101040,101050,101080,101070,101060,101130,101110,101140,101010,101190,101210,101240,101230,101120,101200"

def fetch(keyword, page):
    params = {
        "searchword" : keyword,
        "loc_cd" : LOC_CD,
        "exp_cd" : "1",
        "exp_none" : "y",
        "recruitPage" : page,
        "recruitPageCount" : 40,
    }
    r = requests.get(BASE, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    r.raise_for_status()
    return r.text


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select("div.item_recruit")     #공고 블록 40개, 리스트
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
    return jobs

seen = {}
all_jobs = []
before = 0      #제거 전 건수 세기
for keyword in KEYWORDS:
    for page in range(1, PAGES + 1):
        jobs = parse(fetch(keyword, page))
        before += len(jobs)
        for job in jobs:
            m = re.search(r"rec_idx=(\d+)", job["link"])
            if m is None:
                continue
            rec_idx = m.group(1)            #숫자만 꺼내기
            if rec_idx in seen:
                #이미 적힌 키워드가 아니라면
                if keyword not in seen[rec_idx]["keywords"]:
                    seen[rec_idx]["keywords"].append(keyword)        #목록에 추가
                continue                                            #이 공고는 새로 안 만들고 넘어감
            job["rec_idx"] = rec_idx
            job["keywords"] = [keyword]
            seen[rec_idx] = job
            all_jobs.append(job)
        time.sleep(2.5)  # 2.5초 쉬기
multi = [j for j in all_jobs if len(j["keywords"]) > 1]
print("키워드 2개 이상 공고:", len(multi), "건")
if multi:
    print(multi[0]["title"], multi[0]["keywords"])


print("총", len(all_jobs), "건")
print("제거 전", before, "건 -> 제거 후", len(all_jobs), "건")

filename = f"saramin_{date.today():%Y%m%d}.csv"
for job in all_jobs:
    job["keywords"] = ", ".join(job["keywords"])  #리스트를 문자열로 바꾸기

with open(filename, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "company", "link", "conditions", "deadline", "link", "rec_idx", "keywords"])
    writer.writeheader()
    writer.writerows(all_jobs)
