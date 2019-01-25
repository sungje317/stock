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

ID = "chat_id=476315430&"
text_URL = "https://api.telegram.org/bot641542576:AAHNabxUsCq5nqRmADV2ebNt_NrjjpVl9pg/sendMessage?"
image_URL = "https://api.telegram.org/bot641542576:AAHNabxUsCq5nqRmADV2ebNt_NrjjpVl9pg/sendPhoto"
ID_data = {'chat_id' : "476315430"}
AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
HEADER = {'user-agent':AGENT}
TEMP = "/home/ubuntu/stock/"

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

# 종목 이름을 입력하면 종목에 해당하는 코드를 불러와
# 네이버 금융(http://finance.naver.com)에 넣어줌
def get_url(item_name, code_df):
    code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
    #print("요청 URL = {}".format(url))
    return url

def get_backdata(url):

    try:
        pg_url = '{url}&page={page}'.format(url=url, page=1)
        response = requests.get(pg_url, headers=HEADER)
        html = response.text
        soup = BeautifulSoup(html,'html.parser')
        td = soup.find("td",{"class":"pgRR"})
        end_url = td.find("a",href=True)
        end_url = end_url["href"]
        index = end_url.find("page")
        end = int(end_url[index+5:]) + 1

    except:
        return None, True

    df = pd.DataFrame(columns=['date', 'close', 'diff', 'open', 'high', 'low', 'volume'])
    for page in range(1,3):
        try:
            pg_url = '{url}&page={page}'.format(url=url, page=page)
            df_temp = pd.read_html(pg_url, header=0)[0]
            df_temp = df_temp.dropna()
            df_temp = df_temp.rename(columns={'날짜': 'date', '종가': 'close', '전일비': 'diff', '시가': 'open', '고가': 'high', '저가': 'low', '거래량': 'volume'})
            df_temp[['close', 'diff', 'open', 'high', 'low', 'volume']] = df_temp[['close', 'diff', 'open', 'high', 'low', 'volume']].astype(int)
            df_temp['date'] = pd.to_datetime(df_temp['date'])
            df_temp = df_temp.sort_values(by=['date'], ascending=False)
            df = df.append(df_temp)
        except :
            return None, True
    df = df.reset_index(drop=True)

    df['date'] = pd.to_datetime(df['date'])
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
    df['date'] = mdates.date2num(df['date'])
    df['open'] = pd.to_numeric(df['open'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['close'] = pd.to_numeric(df['close'])

    return df, False

def get_totalsum(name):
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
    return int(Sum)

def get_graph(df, item_name, mental_rate):
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

    path = TEMP+'NanumGothic.ttf'
    fontprop = fm.FontProperties(fname=path, size=16, weight='bold')

    gs = gridspec.GridSpec(3, 3)
    gs.update(hspace=0.05)

    ax = plt.subplot(gs[:-1, :])
    totalsum = get_totalsum(item_name)
    totalsum = int(totalsum * df.loc[1,"close"] / 1000)
    plt.title(item_name + " " + str(totalsum) + "억원 " + "심리도 " + str(mental_rate), fontproperties=fontprop)
    ax1 = plt.subplot(gs[-1, :])

    weekday_candlestick(n_df, ax, fmt='%m/%d', freq=1, width=0.1)
    weekday_barchart(nn_df, ax1, fmt='%m/%d', freq=1, width=0.1)

    ax.plot([0, Last], [n_df[Last - 1][3], n_df[Last - 1][3]], color='g', linestyle='--')

    num_data = str(int(n_df[Last - 1][3]))
    ax.annotate(num_data, xy=(0, n_df[Last - 1][3]), xytext=(1, n_df[Last - 1][1]), weight='bold',
                arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=6))

    plt.savefig(TEMP+'temp.png')

def get_mental(df):
    down_count = 0
    up_count = 0
    down_sum = 0
    up_sum = 0
    mental_rate = 0

    for i in range(5, -1, -1):
        diff = df.close[i] - df.close[i + 1]
        if diff > 0:
            up_count = up_count + 1
            up_sum = up_sum + diff
        elif diff < 0:
            down_count = down_count + 1
            down_sum = down_sum - diff

    if not up_sum + down_sum == 0:
        up_rate = up_sum / (up_sum + down_sum)
        down_rate = down_sum / (up_sum + down_sum)
        mental_rate = (up_count * up_rate - down_count * down_rate) / 6

    return mental_rate

for name in code_df['name']:

#name = "디딤"

    if name.find("스팩") == -1 and name.find("투자") == -1 :
        print(name)
        url = get_url(name, code_df)
        df, empty = get_backdata(url)
        if empty == True:
            continue
        print(df)
        twenty = df["close"].mean()
        today = df[0]["close"]
        print(twenty, today)
        mental_rate = int(get_mental(df) * 100)

        if mental_rate < -50 and twenty < today:
            get_graph(df, name, mental_rate)
            FILE = {'photo': ('temp.png', open(TEMP+'temp.png', "rb"))}
            requests.get(text_URL + ID + "text=비닐하우스")
            requests.post(image_URL, data=ID_data, files=FILE)

        else :
            first_tower = 0
            for i in range(18,-1,-1):
                try:
                    Today = df.loc[i,'volume']
                    Yesterday = df.loc[i+1,'volume']
                except:
                    break

                if first_tower > 0:
                    if mental_rate == -100 :
                        get_graph(df, name, mental_rate)
                        FILE = {'photo': ('temp.png', open(TEMP+'temp.png', "rb"))}
                        requests.get(text_URL + ID + "text=시베리아")
                        requests.post(image_URL, data=ID_data, files=FILE)
                        break
                    if mental_rate < -50 :
                        get_graph(df, name, mental_rate)
                        FILE = {'photo': ('temp.png', open(TEMP+'temp.png', "rb"))}
                        requests.get(text_URL + ID + "text=입동")
                        requests.post(image_URL, data=ID_data, files=FILE)
                        break

                else :
                    if Today > Yesterday * 10 :
                        first_tower = Today

requests.get(text_URL+ID+"text=이상입니다")
