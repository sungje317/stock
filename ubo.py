
from bs4 import BeautifulSoup
import requests
from datetime import date
import matplotlib
matplotlib.use('Agg')
import matplotlib.font_manager as fm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mpl_finance as mpf
import matplotlib.gridspec as gridspec

def weekday_barchart(ohlc_data, ax, fmt='%b %d', freq=7, **kwargs):

    # Convert data to numpy array
    ohlc_data_arr = np.array(ohlc_data)
    ohlc_data_arr2 = np.hstack(
        [np.arange(ohlc_data_arr[:,0].size)[:,np.newaxis], ohlc_data_arr[:,1:]])
    ndays = ohlc_data_arr2[:,0]  # array([0, 1, 2, ... n-2, n-1, n])

    # Convert matplotlib date numbers to strings based on `fmt`
    dates = mdates.num2date(ohlc_data_arr[:,0])
    date_strings = []
    for date in dates:
        date_strings.append(date.strftime(fmt))

    tmp=[]
    for i in range(len(dates)) :
        tmp.append(ohlc_data[i][1])
    ax.bar(ndays[::freq], tmp, 0.35)

    # Format x axis
    ax.set_xticks(ndays[::freq])
    ax.set_xticklabels(date_strings[::freq], rotation=20, ha='right')
    ax.set_xlim(ndays.min(), ndays.max())

def weekday_candlestick(ohlc_data, ax, fmt='%b %d', freq=7, **kwargs):

    # Convert data to numpy array
    ohlc_data_arr = np.array(ohlc_data)
    ohlc_data_arr2 = np.hstack(
        [np.arange(ohlc_data_arr[:,0].size)[:,np.newaxis], ohlc_data_arr[:,1:]])
    ndays = ohlc_data_arr2[:,0]  # array([0, 1, 2, ... n-2, n-1, n])

    # Convert matplotlib date numbers to strings based on `fmt`
    dates = mdates.num2date(ohlc_data_arr[:,0])
    date_strings = []
    for date in dates:
        date_strings.append('')

    # Plot candlestick chart
    mpf.candlestick_ohlc(ax, ohlc_data_arr2, **kwargs, colordown='b', colorup='r')
    ax.set_xticks(ndays[::freq])
    ax.set_xticklabels(date_strings[::freq], ha='right')
    ax.set_xlim(ndays.min(), ndays.max())


DATE = date.today()
TODAY = DATE.strftime("%Y-%m-%d")
TODAY = "2018-10-11"

ID = "chat_id=-235881804&"
text_URL = "https://api.telegram.org/bot641542576:AAHNabxUsCq5nqRmADV2ebNt_NrjjpVl9pg/sendMessage?"
image_URL = "https://api.telegram.org/bot641542576:AAHNabxUsCq5nqRmADV2ebNt_NrjjpVl9pg/sendPhoto"
ID_data = {'chat_id' : "-235881804"}

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=stockMkt', header=0)[0]
# 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
# 우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다.
code_df = code_df[['회사명', '종목코드']]
# 한글로된 컬럼명을 영어로 바꿔준다.
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
print(code_df.head())

# 종목 이름을 입력하면 종목에 해당하는 코드를 불러와
# 네이버 금융(http://finance.naver.com)에 넣어줌
def get_url(item_name, code_df):
    code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
    #print("요청 URL = {}".format(url))
    return url

df = pd.DataFrame()
picked_df = pd.DataFrame(columns=["name","code","yes_last","to_last","percent"])

for name in code_df['name']:

    item_name = name
    code = code_df.query("name=='{}'".format(name))['code'].to_string(index=False)
    url = get_url(item_name, code_df)
    pg_url = '{url}&page={page}'.format(url=url, page=1)
    df = pd.read_html(pg_url, header=0)[0]

    # df.dropna()를 이용해 결측값 있는 행 제거
    df = df.dropna()

    # 한글로 된 컬럼명을 영어로 바꿔줌
    df = df.rename(columns= {'날짜': 'date', '종가': 'close', '전일비': 'diff', '시가': 'open', '고가': 'high', '저가': 'low', '거래량': 'volume'})
    # 데이터의 타입을 int형으로 바꿔줌
    df[['close', 'diff', 'open', 'high', 'low', 'volume']] = df[['close', 'diff', 'open', 'high', 'low', 'volume']].astype(int)
    # 컬럼명 'date'의 타입을 date로 바꿔줌
    df['date'] = pd.to_datetime(df['date'])
    # 일자(date)를 기준으로 오름차순 정렬
    df = df.sort_values(by=['date'], ascending=False)

    if name.find("스팩") == -1:
        try:
            yes_last = int(df.loc[2, 'close'])
            to_last = int(df.loc[1, 'close'])
        except:
            continue
        picked_df.loc[len(picked_df)] = [name, code, yes_last, to_last, (to_last - yes_last) / yes_last]
    print(name)

picked_df = picked_df.sort_values(by=['percent'])
picked_df = picked_df.reset_index(drop=True)
for i in range(1,20):
    print("{}\t{}\t{}\t{}%".format(picked_df.loc[i,'name'], picked_df.loc[i,'yes_last'], picked_df.loc[i,'to_last'], int(picked_df.loc[i, 'percent'] * 100)))