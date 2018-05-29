import pandas as pd
import requests
from bs4 import BeautifulSoup
import requests

ID = "chat_id=-235881804&"
URL = "https://api.telegram.org/bot503225439:AAFVv3WnsASUlJ-SHbBjobaO9dArzN9pCbk/sendMessage?"

texts = []

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
    print("요청 URL = {}".format(url))
    return url

df = pd.DataFrame()

for name in code_df['name']:

    item_name=name
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
    print(df.head())

    try:
        Today = df.loc[1,'volume']
        Close = df.loc[1,'close']
        Low = df.loc[1,'low']
        Yesterday = df.loc[2,'volume']
    except:
        continue

    if Today > Yesterday*10 :

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
        Result = int(Sum) * int(Close)
        Result = str(Result)
        Low = str(Low)

        text = "text=" + name + "%20" + Low + "%20" + Result
        requests.get(URL+ID+text)