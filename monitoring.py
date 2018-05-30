import pandas as pd
import time
import requests

ID = "chat_id=-235881804&"
URL = "https://api.telegram.org/bot503225439:AAFVv3WnsASUlJ-SHbBjobaO9dArzN9pCbk/sendMessage?"

picked_list = pd.DataFrame(columns=["code","low","ins_date","del_date","picked"])

picked_list = pd.read_csv("picked.csv", dtype={'code':object})

def get_url(code):
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
    print("요청 URL = {}".format(url))
    return url

df = pd.DataFrame()


code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=kosdaqMkt', header=0)[0]
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
code_df = code_df[['회사명', '종목코드']]
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})

while True :

    for i in range(len(picked_list)) :
        picked = picked_list.loc[i,"picked"]

        if picked :

            CODE = picked_list.loc[i,"code"]
            NAME = picked_list.loc[i,"name"]
            LOW = picked_list.loc[i,"low"]

            temp_url = get_url(CODE)
            pg_url = '{url}&page={page}'.format(url=temp_url, page=1)
            df = pd.read_html(pg_url, header=0)[0]
            df = df.dropna()
            df = df.rename(columns={'날짜': 'date', '종가': 'close', '전일비': 'diff', '시가': 'open', '고가': 'high', '저가': 'low', '거래량': 'volume'})
            df[['close', 'diff', 'open', 'high', 'low', 'volume']] = df[['close', 'diff', 'open', 'high', 'low', 'volume']].astype(int)
            df['date'] = pd.to_datetime(df['date'])
            #print(df.head())


            NOW = df.loc[1, 'close']

            if int(NOW) < int(LOW):
                DIFF = int(NOW) - int(LOW)
                NOW = str(NOW)
                LOW = str(LOW)
                DIFF = str(DIFF)
                print(NAME, NOW, LOW, DIFF)
                TEXT = "text=" + NAME + "%20" + "저가도달입니다." + "%20" + NOW + "%20" + LOW + "%20" + DIFF
                requests.get(URL + ID + TEXT)
                picked_list.loc[i,"picked"] = 0

    time.sleep(5)
