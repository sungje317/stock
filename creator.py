import pandas as pd

df = pd.DataFrame(columns=["name","code","low","ins_date","del_date","picked"])
df2 = pd.DataFrame(columns=["name","code","low","ins_date","del_date","picked"])
df.loc[0] = ['바른손이앤에이','035620',1785,'2018-05-29','0000-00-00',1]
df.loc[1] = ['예스24','053280',5430,'2018-05-29','0000-00-00',1]
df.loc[2] = ['네오위즈홀딩스','042420',14350,'2018-05-29','0000-00-00',1]
df.loc[3] = ['네오위즈','095660',18400,'2018-05-29','0000-00-00',1]
df.loc[4] = ['마이크로컨텍솔','098120',3920,'2018-05-29','0000-00-00',1]
df.loc[5] = ['지란지교시큐리티','208350',2200,'2018-05-29','0000-00-00',1]
df.loc[6] = ['대아티아이','045390',8490,'2018-05-29','0000-00-00',1]
df.loc[7] = ['키이스트','054780',2805,'2018-05-29','0000-00-00',1]
df.loc[8] = ['오리콤','010470',5510,'2018-05-29','0000-00-00',1]

df.to_csv("picked.csv", encoding='utf-8', index=False)

df2 = pd.read_csv("picked.csv")

print(df2)