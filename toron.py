
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import datetime
import time

ID = "chat_id=476315430&"
AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
HEADER = {'user-agent':AGENT}
send_URL = "https://api.telegram.org/bot641542576:AAHNabxUsCq5nqRmADV2ebNt_NrjjpVl9pg/sendMessage?"

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=kosdaqMkt', header=0)[0]
# 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
# 우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다.
code_df = code_df[['회사명', '종목코드']]
# 한글로된 컬럼명을 영어로 바꿔준다.
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
code_df['last'] = pd.Series(np.zeros(len(code_df['code'])))
code_df = code_df.set_index("name")
print(code_df.head())

# 종목 이름을 입력하면 종목에 해당하는 코드를 불러와
# 네이버 금융(http://finance.naver.com)에 넣어줌
def get_url_naver(item_name, code_df):
    code = code_df.loc[item_name,"code"]
    url = 'https://finance.naver.com/item/board.nhn?code={code}'.format(code=code)
    #print("요청 URL = {}".format(url))
    return url

picked_df = pd.DataFrame(columns=["name","sum","mk_sum","surplus","index"])

end_time = datetime.datetime.now() + datetime.timedelta(hours=7)

while datetime.datetime.now() < end_time :

    for name in code_df.index:

        item_name = name
        url = get_url_naver(item_name, code_df)
        last = code_df.loc[name,"last"]
        last = int(last)


        if name.find("스팩") == -1:
            try:
                html = requests.get(url).text
                soup = BeautifulSoup(html, 'html.parser')
                list = soup.find_all("td", {"class": "title"})

                toron_list = pd.DataFrame(columns=["title", "nid"])
                for e in list:
                    atag = e.find("a")
                    title = atag.text
                    title = title.replace("\n", "")
                    title = title.replace("\t", "")
                    parser = title.split("[")
                    parser = parser[0]

                    link = atag.attrs['href']
                    s_index = link.find("nid")
                    s_index = s_index + 4
                    e_index = link.find("&st")
                    nid = link[s_index:e_index]
                    nid = int(nid)

                    if not parser.find("이낙연") == -1 or not parser.find("황교안") == -1:
                        toron_list.loc[len(toron_list)] = [parser, nid]

                toron_list = toron_list.sort_values(by=["nid"])
                toron_list = toron_list.reset_index(drop=True)

                for idx in range(len(toron_list)):
                    if last < toron_list.loc[idx, "nid"] :
                        last = toron_list.loc[idx, "nid"]
                        title = toron_list.loc[idx,"title"]

                        text = name + "> " + title

                        requests.get(send_URL+ID+"text="+text)
                        print(name, toron_list.loc[idx,"title"], last)

                code_df.loc[name,"last"] = last

            except:
                continue