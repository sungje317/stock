import requests

ID = "476315430"

FILE = {'photo': ('download.png', open('download.png',"rb"))}
URL = "https://api.telegram.org/bot503225439:AAFVv3WnsASUlJ-SHbBjobaO9dArzN9pCbk/sendPhoto"

data = {'chat_id' : ID}


result = requests.post(URL, data = data, files=FILE)

print(result.text)
