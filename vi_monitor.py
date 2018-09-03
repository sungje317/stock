import time
import requests
import datetime
import json

OTP_URL = "http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx?bld=MKD%2F10%2F1002%2F10020408%2Fmkd10020408&name=form&_" + str(int(time.time()*1000))
AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
HEADER = {'user-agent':AGENT, 'X-Requested-With': 'XMLHttpRequest'}
DATE = datetime.date.today()
TODAY = DATE.strftime("%Y%m%d")
picked = []

SEARCH_URL = "http://marketdata.krx.co.kr/contents/MKD/99/MKD99000001.jspx"
ID = "chat_id=476315430&"
SEND_URL = "https://api.telegram.org/bot641542576:AAHNabxUsCq5nqRmADV2ebNt_NrjjpVl9pg/sendMessage?"

OTP = requests.get(OTP_URL,headers=HEADER)
OTP = OTP.text
print(TODAY)

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
#print(value.text)
value = json.loads(value.text)

end_time = datetime.datetime.now() + datetime.timedelta(hours=7)
while datetime.datetime.now() < end_time :
    for item in value['result']:
        vi_activated = item['isu_abbrv']
        print(vi_activated)
        if vi_activated not in picked :
            requests.get(SEND_URL + ID + "text=vi발동!!!!" + vi_activated)
            picked.append(vi_activated)

    time.sleep(1)