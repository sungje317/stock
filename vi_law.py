import time
import requests
import datetime
import json
import pandas as pd
from bs4 import BeautifulSoup

OTP_URL = "http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx?bld=MKD%2F10%2F1002%2F10020408%2Fmkd10020408&name=form&_" + str(int(time.time()*1000))
AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
HEADER = {'user-agent':AGENT, 'X-Requested-With': 'XMLHttpRequest'}
DATE = datetime.date.today()
TODAY = DATE.strftime("%Y%m%d")

SEARCH_URL = "http://marketdata.krx.co.kr/contents/MKD/99/MKD99000001.jspx"
ID = "chat_id=476315430&"
SEND_URL = "https://api.telegram.org/bot641542576:AAHNabxUsCq5nqRmADV2ebNt_NrjjpVl9pg/sendMessage?"
URL = "http://www.paxnet.co.kr/tbbs/list?tbbsType=L&id=N00820"
LINK = "http://www.paxnet.co.kr/tbbs/view?id=N00820&seq="
AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
HEADER = {'user-agent':AGENT}

print(TODAY)

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

end_time = datetime.datetime.now() + datetime.timedelta(hours=7)
count = 0
order = 0

while datetime.datetime.now() < end_time :
    print(count)
    count = count + 1
    OTP = requests.get(OTP_URL, headers=HEADER)
    OTP = OTP.text
    REQUEST = {
        'mkt_tp_cd': 'ALL',
        'vi_kind_cd': 'ALL',
        'isu_cdnm': '전체',
        'isu_cd': '',
        'isu_nm': '',
        'isu_srt_cd': '',
        'fr_work_dt': TODAY,
        'to_work_dt': TODAY,
        'pagePath': '/contents/MKD/10/1002/10020408/MKD10020408.jsp',
        'code': OTP,
        'pageFirstCall': 'Y'
    }
    value = requests.post(SEARCH_URL, REQUEST, HEADER)
    value = json.loads(value.text)
    for item in value['result']:
        print(item)
        vi_activated = item['isu_abbrv']
        vi_percent = float(item['vi_tg_prc_divrg_rt'])
        vi_ord = int(item['isu_ord'])
        if vi_ord > order :
            order = vi_ord
            if not count == 1 :
                if vi_percent > 0 :
                    print(vi_activated)
                    for page in range(1, 4):
                        pg_url = '{url}&page={page}'.format(url=URL, page=page)
                        response = requests.get(pg_url, headers=HEADER)
                        html = response.text
                        soup = BeautifulSoup(html, 'html.parser')
                        name_list = soup.find_all("span", {"class": "flag-opt"})
                        title_list = soup.find_all("a", {"class": "best-title"})
                        href_list = soup.find_all("a", {"class": "best-title"}, href=True)

                        for index in range(len(name_list)):
                            name = name_list[index].text
                            name = name[1:-1]
                            title = title_list[index].text
                            href = href_list[index]["href"]
                            href = href.split("(")
                            href = href[1]
                            href = href[:-2]

                            if not name.find(vi_activated) == -1:
                                ID_data = {'chat_id': "-322150068", 'text': LINK + href}
                                requests.post(SEND_URL, data=ID_data)