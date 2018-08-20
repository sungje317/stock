import pandas as pd
from bs4 import BeautifulSoup
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


ID = "chat_id=-235881804&"
URL = "https://api.telegram.org/bot641542576:AAHNabxUsCq5nqRmADV2ebNt_NrjjpVl9pg/sendMessage?"
image_URL = "https://api.telegram.org/bot641542576:AAHNabxUsCq5nqRmADV2ebNt_NrjjpVl9pg/sendPhoto"
ID_data = {'chat_id' : "-235881804"}

picked_list = []
picked_feature = []
results = []

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType=kosdaqMkt', header=0)[0]
# 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)
# 우리가 필요한 것은 회사명과 종목코드이기 때문에 필요없는 column들은 제외해준다.
code_df = code_df[['회사명', '종목코드']]
# 한글로된 컬럼명을 영어로 바꿔준다.
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'})
print(code_df.head())



for name in code_df['name'] :

    if name.find("스팩") == -1 :

        code = code_df.query("name=='{}'".format(name))['code'].to_string(index=False)
        inst_URL = "http://finance.naver.com/item/frgn.nhn?code=" + code
        html = requests.get(inst_URL).text

        soup = BeautifulSoup(html, 'html.parser')

        inst_area = soup.find("table", {"summary": "외국인 기관 순매매 거래량에 관한표이며 날짜별로 정보를 제공합니다."})
        inst_table = inst_area.find_all("td",{"width":"66"})

        sum_URL = "http://finance.naver.com/item/sise.nhn?code=" + code

        html = requests.get(sum_URL).text

        soup = BeautifulSoup(html, 'html.parser')

        sum_area = soup.find("table", {"summary": "시가총액 정보"})
        sum_table = sum_area.find_all("td")
        value_element = sum_table[0]
        value = value_element.find("em").text
        value = value.replace("\n", "")
        value = value.replace("\t", "")
        print(value)
        sum_element = sum_table[2]
        SUM = sum_element.find("em").text
        SUM = SUM.replace(",","")
        SUM = int(SUM)

        inst_SUM = 0
        inst = []
        i = 0
        for table in inst_table :
            try :
                TMP = table.find("span").text
            except :
                continue

            TMP = TMP.replace(",","")
            inst_SUM = inst_SUM + int(TMP)
            inst.append(inst_SUM)
            i = i + 1

        print(name, inst_SUM, SUM, i)
        if i > 19 :
            for i in range(3, 20, 4):
                if inst[i] / SUM * 100 > int(i / 5) + 1 :
                    TEXT = "text=" + name + "%20" + str(inst_SUM) + "%20" + str(SUM)
                    results.append(TEXT)
                    for j in range(3, 20, 4):
                        inst[j] = int(inst[j] / SUM * 100)
                    picked_feature.append([name, value, inst[3], inst[7], inst[11], inst[15], inst[19]])
                    #picked_list.append("{} {}% {}% {}% {}% {}% {}".format(name, inst[3], inst[7], inst[11], inst[15], inst[19], SUM))
                    break

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

TEXT = "text=" + "20일간 기관 매수세 입니다."
requests.get(URL+ID+TEXT)

for feature in picked_feature :
    print(feature)
    fig = plt.figure(facecolor='white')
    ax = fig.add_subplot(1,1,1)
    x = ['20','16','12','8','4']
    negative_data = []
    positive_data = []
    for i in range(6, 1, -1):

        if feature[i] > 0:
            positive_data.append(int(feature[i] / i * 100))
            negative_data.append(0)
        else:
            positive_data.append(0)
            negative_data.append(int(feature[i] / i * 100))

    print(positive_data)
    print(x)
    rect1 = ax.bar(x, negative_data, width=0.5, color = 'b')
    rect2 = ax.bar(x, positive_data, width=0.5, color = 'r')

    i = 6
    for rect in rect1 :
        height = rect.get_height()
        if not height == 0 :
            ax.text(rect.get_x() + rect.get_width() / 2., 1.05 * height,
                    '%d%%' % feature[i],
                    ha='center', va='bottom')
        i = i - 1

    i = 6
    for rect in rect2 :
        height = rect.get_height()
        if not height == 0 :
            ax.text(rect.get_x() + rect.get_width() / 2., 1.05 * height,
                    '%d%%' % feature[i],
                    ha='center', va='bottom')
        i = i - 1

    plt.ylim(-200, 200)

    path = '/home/ubuntu/stock/NanumGothic.ttf'
    fontprop = fm.FontProperties(fname=path, size=16, weight='bold')
    plt.title("{} {}억".format(feature[0], feature[1]), fontproperties=fontprop)

    plt.savefig('/home/ubuntu/stock/temp.png')
    FILE = {'photo': ('temp.png', open('/home/ubuntu/stock/temp.png', "rb"))}
    requests.post(image_URL, data=ID_data, files=FILE)

    print("{} {}억 {}% {}% {}% {}% {}%".format(feature[0], feature[1], feature[2], feature[3], feature[4], feature[5], feature[6]))
