#!/home/ubuntu/miniconda3/bin/python3

from bs4 import BeautifulSoup
import requests
from datetime import date
import matplotlib
matplotlib.use('Agg')
import matplotlib.font_manager as fm
import pandas as pd
import json
import datetime
import time

DATE = date.today()
TODAY = DATE.strftime("%Y-%m-%d")

ID = "chat_id=-322150068&"
ID = "chat_id=476315430&"
text_URL = "https://api.telegram.org/bot641542576:AAHNabxUsCq5nqRmADV2ebNt_NrjjpVl9pg/sendMessage?"
image_URL = "https://api.telegram.org/bot641542576:AAHNabxUsCq5nqRmADV2ebNt_NrjjpVl9pg/sendPhoto"
ID_data = {'chat_id' : "-322150068"}
ID_data = {'chat_id' : "476315430"}
AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
HEADER = {'user-agent':AGENT, 'apikey':'vSBA8hHLWw6Nm8ynJC4CbsOkcdIGjHia'}
TEMP = "/home/ubuntu/stock/"
TEMP = "/Users/parksang-yeon/stock/"
APIURL = 'http://133.186.146.218:8000/class/data?'
fontprop = fm.FontProperties(fname=TEMP+'BMDOHYEON_ttf.ttf', size=16, weight='bold')

def get_class(Class, Subclass):
    RealURL = APIURL + 'Class=' + Class + '&Subclass=' + Subclass
    result = requests.get(RealURL, headers=HEADER)
    result = result.text
    result = json.loads(result)
    result = result[0]
    return result["Cname"], result["Sname"]

code_df_kosdaq = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=kosdaqMkt', header=0)[0]
code_df_kosdaq.종목코드 = code_df_kosdaq.종목코드.map('{:06d}'.format)
code_df_kosdaq = code_df_kosdaq[['회사명', '종목코드']]
code_df_kosdaq = code_df_kosdaq.rename(columns={'회사명': 'name', '종목코드': 'code'})
print(code_df_kosdaq.head())

code_df_kospi = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=stockMkt', header=0)[0]
code_df_kospi.종목코드 = code_df_kospi.종목코드.map('{:06d}'.format)
code_df_kospi = code_df_kospi[['회사명', '종목코드']]
code_df_kospi = code_df_kospi.rename(columns={'회사명': 'name', '종목코드': 'code'})
print(code_df_kospi.head())

code_df = code_df_kosdaq
code_df = code_df.append(code_df_kospi)

stock_code = pd.read_csv(TEMP+"stock_code.csv", dtype=str)

def get_url(code, thistime):
    url = 'http://finance.naver.com/item/sise_time.nhn?code={code}&thistime={thistime}'.format(code=code,thistime=thistime)
    return url

def get_backdata(url):

    try:
        df = pd.read_html(url, header=0)[0]
        df = df.dropna()
        df = df.rename(columns={'체결시각': 'time', '체결가': 'price', '전일비': 'diff', '매도': 'sell', '매수': 'buy', '거래량': 'volume', '변동량': 'change'})
        df[['price', 'diff', 'sell', 'buy', 'volume', 'change']] = df[['price', 'diff', 'sell', 'buy', 'volume', 'change']].astype(int)
        df = df.reset_index(drop=True)
    except :
        return None, True

    return df, False

def get_totalsum(code):
    sum_URL = "http://finance.naver.com/item/sise.nhn?code=" + code

    html = requests.get(sum_URL).text

    soup = BeautifulSoup(html, 'html.parser')

    sum_area = soup.find("table", {"summary": "시가총액 정보"})
    sum_table = sum_area.find_all("td")
    sum_element = sum_table[2]
    Sum = sum_element.find("em").text
    Sum = Sum.replace(",", "")
    Sum = Sum[:-5]
    return int(Sum)


start_time = datetime.datetime.now()
end_time = start_time + datetime.timedelta(minutes=40)
count = 0
min = 0
today = date.today().strftime("%Y%m%d")

while datetime.datetime.now() < end_time :
    print(count)
    count = count + 1

    minStr = str(min).zfill(2)
    thistime = today + "15" + minStr + "0000"

    for index in range(stock_code.shape[0]):

        code = stock_code.loc[index]["StockCode"]
        name = stock_code.loc[index]["StockName"]
        # Class = stock_code.loc[index]["Class"]
        # Subclass = stock_code.loc[index]["Subclass"]
        #
        # Class, Subclass = get_class(Class, Subclass)

        print(name)

        if name.find("스팩") == -1 :

            try:
                total_sum = str(get_totalsum(code))
            except:
                continue

            url = get_url(code, thistime)
            df, empty = get_backdata(url)
            if empty == True:
                continue

            print(df)
            try:
                after = int(df.loc[0, 'change']) + int(df.loc[1, 'change']) + int(df.loc[2, 'change'])
                before = int(df.loc[3, 'change']) + int(df.loc[4, 'change']) + int(df.loc[5, 'change'])
                price = str(df.loc[0, 'price'])
                diff = str(round((float(df.loc[0, 'price']) - float(df.loc[3, 'price'])) * 100 / float(df.loc[3, 'price']),2))
            except:
                continue

            if before * 10 < after :
                times = str(int(after / before))
                requests.get(text_URL + ID + "text="+ "15:" + minStr + " " + name + " " + price + " " + times + "배 " + diff + "% " + total_sum + "억")

    min = min + 3

    gap = start_time + datetime.timedelta(minutes=min) - datetime.datetime.now()
    time.sleep(int(gap.seconds))
