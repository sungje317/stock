from bs4 import BeautifulSoup
import requests
import datetime
import time
import pandas as pd

URL = 'http://www.etoday.co.kr/news/hotissue/newsman_txt.php?eid=minori3032'
send_URL = 'https://api.telegram.org/bot503225439:AAFVv3WnsASUlJ-SHbBjobaO9dArzN9pCbk/sendMessage?'
ID = "chat_id=-235881804&"
AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
HEADER = {'user-agent':AGENT}

def get_list():

    df = pd.DataFrame(columns=['time', 'title', 'contents'])

    html = requests.get(URL, headers=HEADER).text
    soup = BeautifulSoup(html, 'html.parser')
    area = soup.find("ul", {"class": "news_lst news_lst2"})
    list = area.find_all("li")

    for element in list :
        title = element.find("a", {"class": "tit"}).text
        contents = element.find("p").find("a").text
        time = element.find("span").text
        time = time.replace(" ","")
        time = datetime.datetime.strptime(time,"%Y-%m-%d%H:%M")
        df.loc[df.shape[0]] = [time, title, contents]

    return df

NOW = datetime.datetime.now()
END = NOW + datetime.timedelta(hours = 8)

while now < END :
    df = get_list()
    now = datetime.datetime.now() - datetime.timedelta(minutes = 1)

    for i in range(df.shape[0]) :
        if df.loc[i, 'time'] > now :
            if df.loc[i, 'title'].find('[특징주]') > -1 :
                TEXT = 'text=' + df.loc[i, 'title']
                requests.get(send_URL+ID+TEXT)
                TEXT = 'text=' + df.loc[i, 'contents']
                requests.get(send_URL+ID+TEXT)

    time.sleep(59)


