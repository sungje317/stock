import pandas as pd
from bs4 import BeautifulSoup
import requests

ID = "chat_id=-235881804&"
URL = "https://api.telegram.org/bot503225439:AAFVv3WnsASUlJ-SHbBjobaO9dArzN9pCbk/sendMessage?"

picked_list = []
results = []

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=kosdaqMkt', header=0)[0]
# 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
# 우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다.
code_df = code_df[['회사명', '종목코드']]
# 한글로된 컬럼명을 영어로 바꿔준다.
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
print(code_df.head())



for name in code_df['name'] :

    if name.find("스팩") == -1 :

        code = code_df.query("name=='{}'".format(name))['code'].to_string(index=False)
        inst_URL = "http://finance.naver.com/item/frgn.nhn?code=" + code
        html = requests.get(inst_URL).text

        soup = BeautifulSoup(html, 'html.parser')

        inst_area = soup.find("table", {"summary": "외국인 기관 순매매 거래량에 관한표이며 날짜별로 정보를 제공합니다."})
        inst_table = inst_area.find_all("td",{"width":"66"})

        inst_SUM = 0
        i=0
        for table in inst_table :
            try :
                TMP = table.find("span").text
            except :
                continue

            TMP = TMP.replace(",","")
            inst_SUM = inst_SUM + int(TMP)

        sum_URL = "http://finance.naver.com/item/sise.nhn?code=" + code

        html = requests.get(sum_URL).text

        soup = BeautifulSoup(html, 'html.parser')

        sum_area = soup.find("table", {"summary": "시가총액 정보"})
        sum_table = sum_area.find_all("td")
        sum_element = sum_table[2]
        SUM = sum_element.find("em").text
        SUM = SUM.replace(",","")
        SUM = int(SUM)

        print(name, inst_SUM, SUM)

        if inst_SUM * 20 > SUM :
            TEXT = "text=" + name + "%20" + str(inst_SUM) + "%20" + str(SUM)
            results.append(TEXT)
            picked_list.append("{} {} {}".format(name, inst_SUM, SUM))



print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

TEXT = "text=" + "20일내"+"%20"+"기관매수가" + "%20" + "총발행수대비" + "%20" + "5%25이상" + "종목입니다."
requests.get(URL+ID+TEXT)

for text in picked_list :
    print(text)

for text in results:
    requests.get(URL + ID + text)

TEXT = "text=이상입니다."
requests.get(URL + ID + TEXT)