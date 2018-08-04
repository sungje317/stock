import pandas as pd
from bs4 import BeautifulSoup
import requests

data = pd.DataFrame(columns=['name', 'sum', 'inst', 'volume'])

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=kosdaqMkt', header=0)[0]
# 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
# 우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다.
code_df = code_df[['회사명', '종목코드']]
# 한글로된 컬럼명을 영어로 바꿔준다.
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
print(code_df.head())

def get_sum (code):
    sum_URL = "http://finance.naver.com/item/sise.nhn?code=" + code
    html = requests.get(sum_URL).text
    soup = BeautifulSoup(html, 'html.parser')
    sum_area = soup.find("table", {"summary": "시가총액 정보"})
    sum_table = sum_area.find_all("td")
    sum_element = sum_table[2]
    SUM = sum_element.find("em").text
    SUM = SUM.replace(",", "")
    return int(SUM)

def get_major_stakeholder (code):
    major_URL = "https://companyinfo.stock.naver.com/v1/company/c1010001.aspx?cmp_cd=" + code
    html = requests.get(major_URL).text
    soup = BeautifulSoup(html, 'html.parser')
    major_area = soup.find("table", {"id": "cTB13"})
    major_table = major_area.find_all("td", {"class": "line num"})

    SUM = 0

    for major_element in major_table:
        element = major_element.text
        try:
            element=element.replace(",", "")
            element = int(element)
        except:
            break
        SUM = SUM + element

    return SUM

for name in code_df['name'] :

    if name.find("스팩") == -1 :

        code = code_df.query("name=='{}'".format(name))['code'].to_string(index=False)
        inst_URL = "http://finance.naver.com/item/frgn.nhn?code=" + code
        html = requests.get(inst_URL).text

        soup = BeautifulSoup(html, 'html.parser')

        inst_area = soup.find("table", {"summary": "외국인 기관 순매매 거래량에 관한표이며 날짜별로 정보를 제공합니다."})
        inst_table = inst_area.find_all("td",{"width":"66"})

        sum_URL = "http://finance.naver.com/item/sise.nhn?code=" + code

        html = requests.get(sum_URL).text

        soup = BeautifulSoup(html, 'html.parser')

        sum_area = soup.find("table", {"summary": "시가총액 정보"})
        sum_table = sum_area.find_all("td")
        sum_element = sum_table[2]
        SUM = sum_element.find("em").text
        SUM = SUM.replace(",","")
        SUM = int(SUM)

        INST = get_major_stakeholder(code)

        try :
            VOL = inst_table[0].find("span").text
        except :
            continue
        VOL = VOL.replace(",","")
        VOL = int(VOL)

        data.loc[data.shape[0]] = [name, SUM, INST, VOL]
        print(name, SUM, INST, VOL)

data.to_csv('vol_data.csv')
