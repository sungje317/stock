from __future__ import unicode_literals
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mpl_finance as mpf
import matplotlib.font_manager as fm
import matplotlib.gridspec as gridspec

def weekday_barchart(ohlc_data, ax, fmt='%b %d', freq=7, **kwargs):

    # Convert data to numpy array
    #dtype =  [('date', float),('open', float),('high', float),('low', float),('close', float),('volume', float)]
    ohlc_data_arr = np.array(ohlc_data)
    ohlc_data_arr2 = np.hstack(
        [np.arange(ohlc_data_arr[:,0].size)[:,np.newaxis], ohlc_data_arr[:,1:]])
    ndays = ohlc_data_arr2[:,0]  # array([0, 1, 2, ... n-2, n-1, n])

    # Convert matplotlib date numbers to strings based on `fmt`
    dates = mdates.num2date(ohlc_data_arr[:,0])
    date_strings = []
    for date in dates:
        date_strings.append(date.strftime(fmt))

    tmp = []
    for i in range(len(dates)) :
        tmp.append(ohlc_data[i][1])

    ax.bar(ndays[::freq], tmp, 0.2)

    # Format x axis
    ax.set_xticks(ndays[::freq])
    ax.set_xticklabels(date_strings[::freq], rotation=20, ha='right')
    ax.set_xlim(ndays.min(), ndays.max())

def weekday_candlestick(ohlc_data, ax, fmt='%b %d', freq=7, **kwargs):

    # Convert data to numpy array
    #dtype =  [('date', float),('open', float),('high', float),('low', float),('close', float),('volume', float)]
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


code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=kosdaqMkt', header=0)[0]
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
code_df = code_df[['회사명', '종목코드']]
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})

def get_url(item_name, code_df):
    code = code_df.query("name=='{}'".format(item_name))['code'].to_string(index=False)
    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)
    return url

df = pd.DataFrame()
picked_df = pd.DataFrame(columns=["name","code","low","ins_date","del_date","picked"])

item_name = "부방"
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
df['date'] = pd.to_datetime(df['date'],format="%Y-%m-%d")
df['date'] = mdates.date2num(df['date'])
df['open'] = pd.to_numeric(df['open'])
df['high'] = pd.to_numeric(df['high'])
df['low'] = pd.to_numeric(df['low'])
df['close'] = pd.to_numeric(df['close'])
df['volume'] = pd.to_numeric(df['volume'])

df = df.sort_values(by='date')

n_df = df[['date','open','high','low','close']].values
nn_df = df[['date','volume']].values

n_df = np.insert(n_df,0,[n_df[0][0]-1,np.NaN,np.NaN,np.NaN,np.NaN], axis=0)
Last = int(n_df.shape[0])
Last_day = n_df[Last-1][0] + 1
n_df = np.insert(n_df,Last,[Last_day,np.NaN,np.NaN,np.NaN,np.NaN], axis=0)

nn_df = np.insert(nn_df,0,[nn_df[0][0]-1,0], axis=0)
Last = int(nn_df.shape[0])
Last_day = nn_df[Last-1][0] + 1
nn_df = np.insert(nn_df,Last,[Last_day,0], axis=0)

path = '/Library/Fonts/Arial Unicode.ttf'
fontprop = fm.FontProperties(fname=path, size=16, weight='bold')

gs = gridspec.GridSpec(3, 3)
gs.update(hspace=0.05)

ax = plt.subplot(gs[:-1, :])
plt.title(item_name, fontproperties=fontprop)
ax1 = plt.subplot(gs[2:, :])

weekday_candlestick(n_df, ax, fmt='%m/%d', freq=1, width=0.2)
weekday_barchart(nn_df, ax1, fmt='%m/%d', freq=1, width=0.1)

ax.plot([0,Last],[n_df[Last-1][3],n_df[Last-1][3]],color='g',linestyle='--')

num_data = str(int(n_df[Last-1][3]))
ax.annotate(num_data, xy=(0,n_df[Last-1][3]), xytext= (1,n_df[Last-1][1]), weight='bold', arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=6))


plt.show()

