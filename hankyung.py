from bs4 import BeautifulSoup
import requests
from datetime import date
import pandas as pd

ID = "chat_id=-235881804&"
send_URL = "https://api.telegram.org/bot503225439:AAFVv3WnsASUlJ-SHbBjobaO9dArzN9pCbk/sendMessage?"

URL = 'http://hkconsensus.hankyung.com/apps.analysis/analysis.list?skinType=business&'
AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
DATE = date.today()
TODAY = DATE.strftime("%Y-%m-%d")
#TODAY = '2018-06-29'

URL = URL + "sdate=" + TODAY + "&edate=" + TODAY
HEADER = {'user-agent':AGENT}

df = pd.DataFrame(columns=['name', 'code', 'content', 'value'])

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=kosdaqMkt', header=0)[0]
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
code_df = code_df[['회사명', '종목코드']]
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})

picked_list = []

for i in range(1,6,1) :
    try :
        page_URL = URL + "&now_page=" + str(i)
        response = requests.get(page_URL, headers=HEADER)
        response.encoding = 'euc-kr'
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find_all("td", class_= "text_l")
    except :
        continue

    for element in table :
        content = element.find("a").text
        parse = content.split("(")
        parse = parse[1].split(")")
        try :
            code = parse[0]
            name = code_df.query("code=='{}'".format(code))['name'].to_string(index=False)
        except :
            continue

        if not name == 'Series([], )' :

            sum_URL = "http://finance.naver.com/item/sise.nhn?code=" + code
            html = requests.get(sum_URL).text
            soup = BeautifulSoup(html, 'html.parser')

            sum_area = soup.find("table", {"summary": "시가총액 정보"})
            sum_table = sum_area.find_all("td")
            value_element = sum_table[0]
            value = value_element.find("em").text
            value = value.replace("\n", "")
            value = value.replace("\t", "")

            print(name, code, value)
            value_int = value.replace(",","")
            try :
                value_int = int(value_int)
            except :
                continue
            if value_int < 3000 :
                picked_list.append([name, code, value, content])

TEXT = "text=" + TODAY + " 한경컨센서스 관련주식입니다."
requests.get(send_URL+ID+TEXT)

for picked in picked_list :
    TEXT = "text=" + picked[0] + " "  + picked[2] + "억 " + picked[3]
    requests.get(send_URL+ID+TEXT)
    print(picked)