import requests
from bs4 import BeautifulSoup

url = "https://www.saramin.co.kr/zf_user/search/recruit?searchword=데이터분석&loc_mcd=101000&exp_cd=1&recruitPageCount=40"
response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
n = len(BeautifulSoup(response.text, "html.parser").select("div.item_recruit"))
print("상태코드:", response.status_code, "| 공고 수:", n, "| 응답길이:", len(response.text))