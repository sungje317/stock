#!/home/ubuntu/miniconda3/bin/python3

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

ID = "chat_id=-235881804&"
text_URL = "https://api.telegram.org/bot641542576:AAHNabxUsCq5nqRmADV2ebNt_NrjjpVl9pg/sendMessage?"
image_URL = "https://api.telegram.org/bot641542576:AAHNabxUsCq5nqRmADV2ebNt_NrjjpVl9pg/sendPhoto"
ID_data = {'chat_id' : "-235881804"}

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=kosdaqMkt', header=0)[0]
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
picked_df = pd.DataFrame(columns=["name","code","low","ins_date","del_date","picked"])

for name in code_df['name']:

    item_name = name
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
    # 상위 5개 데이터 확인
    #print(df.head())


    try:
        Today = df.loc[1,'volume']
        Close = df.loc[1,'close']
        Low = df.loc[1,'low']
        Yesterday = df.loc[2,'volume']
        Diff = df.loc[1,'diff']
    except:
        continue

    if Today > Yesterday*10 :
        if not Yesterday == 0 :
            if Diff > 0 :
                if name.find("스팩") == -1:

                    code = code_df.query("name=='{}'".format(name))['code'].to_string(index=False)
                    sum_URL = "http://finance.naver.com/item/sise.nhn?code=" + code

                    html = requests.get(sum_URL).text

                    soup = BeautifulSoup(html, 'html.parser')

                    sum_area = soup.find("table", {"summary": "시가총액 정보"})
                    sum_table = sum_area.find_all("td")
                    sum_element = sum_table[2]
                    Sum = sum_element.find("em").text
                    Sum = Sum.replace(",", "")
                    Sum = Sum[:-5]
                    Result = int(int(Sum) * int(Close) / 1000)

                    Mul = int(Today / Yesterday)
                    Result = str(Result)
                    Low = str(Low)
                    Mul = str(Mul)

                    text = "text=" + name + "%20" + Mul + "배" + "%20" + Low + "%20" + Result + "억원"
                    print(name, Mul, Low, Result)

                    requests.get(text_URL+ID+text)

                    picked_df.loc[len(picked_df)] = [name,code,Low,TODAY,'0000-00-00',1]

                    df['date'] = pd.to_datetime(df['date'])
                    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
                    df['date'] = mdates.date2num(df['date'])
                    df['open'] = pd.to_numeric(df['open'])
                    df['high'] = pd.to_numeric(df['high'])
                    df['low'] = pd.to_numeric(df['low'])
                    df['close'] = pd.to_numeric(df['close'])

                    df = df.sort_values(by='date')

                    n_df = df[['date', 'open', 'high', 'low', 'close']].values
                    nn_df = df[['date', 'volume']].values

                    n_df = np.insert(n_df, 0, [n_df[0][0] - 1, np.NaN, np.NaN, np.NaN, np.NaN], axis=0)
                    Last = int(n_df.shape[0])
                    Last_day = n_df[Last - 1][0] + 1
                    n_df = np.insert(n_df, Last, [Last_day, np.NaN, np.NaN, np.NaN, np.NaN], axis=0)

                    nn_df = np.insert(nn_df, 0, [nn_df[0][0] - 1, 0], axis=0)
                    Last = int(nn_df.shape[0])
                    Last_day = nn_df[Last - 1][0] + 1
                    nn_df = np.insert(nn_df, Last, [Last_day, 0], axis=0)

                    path = '/home/ubuntu/stock/NanumGothic.ttf'
                    fontprop = fm.FontProperties(fname=path, size=16, weight='bold')

                    gs = gridspec.GridSpec(3, 3)
                    gs.update(hspace=0.05)

                    ax = plt.subplot(gs[:-1, :])
                    plt.title(item_name + " " + Result + "억원", fontproperties=fontprop)
                    ax1 = plt.subplot(gs[-1, :])

                    weekday_candlestick(n_df, ax, fmt='%m/%d', freq=1, width=0.1)
                    weekday_barchart(nn_df, ax1, fmt='%m/%d', freq=1, width=0.1)

                    ax.plot([0, Last], [n_df[Last - 1][3], n_df[Last - 1][3]], color='g', linestyle='--')

                    num_data = str(int(n_df[Last - 1][3]))
                    ax.annotate(num_data, xy=(0, n_df[Last - 1][3]), xytext=(1, n_df[Last - 1][1]), weight='bold',
                                arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=6))

                    plt.savefig('/home/ubuntu/stock/temp.png')

                    FILE = {'photo': ('temp.png', open('/home/ubuntu/stock/temp.png', "rb"))}
                    requests.post(image_URL, data=ID_data, files=FILE)

with open('/home/ubuntu/stock/picked.csv','a') as f:
    picked_df.to_csv(f, header=False, index=False)

text = "이상입니다."
requests.get(text_URL+ID+text)
