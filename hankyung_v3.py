from bs4 import BeautifulSoup
import requests
from datetime import date
import pandas as pd

ID = "chat_id=476315430&"
send_URL = "https://api.telegram.org/bot641542576:AAHNabxUsCq5nqRmADV2ebNt_NrjjpVl9pg/sendMessage?"
doc_URL = "https://api.telegram.org/bot641542576:AAHNabxUsCq5nqRmADV2ebNt_NrjjpVl9pg/sendDocument"

URL = 'http://hkconsensus.hankyung.com/apps.analysis/analysis.list?&sdate=2018-01-01&edate=2018-09-30&search_value=&search_text=%B1%E8%B5%CE%C7%F6'
AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"

HEADER = {'user-agent':AGENT}

df = pd.DataFrame(columns=['name','code','date'])

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=kosdaqMkt', header=0)[0]
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
code_df = code_df[['회사명', '종목코드']]
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})

for i in range(1,8,1) :
    try :
        page_URL = URL + "&now_page=" + str(i)
        response = requests.get(page_URL, headers=HEADER)
        response.encoding = 'euc-kr'
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        t_list = soup.find_all("tr")

    except :
        continue

    #print(t_list)
    for table in t_list :
        e_list = table.find_all("td")
        count=0
        try :
            date = e_list[0].text
            doc_element = e_list[2]
        except :
            continue

        text = doc_element.find("strong").text

        try :
            parse = text.split("(")
            parse = parse[1].split(")")
            code = parse[0]
            name = code_df.query("code=='{}'".format(code))['name'].to_string(index=False)
        except :
            continue

        if not name == 'Series([], )' :
            df.loc[len(df)] = [name, code, date]

df.to_csv('kimPicks.csv', index=False)