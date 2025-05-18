import requests
from bs4 import BeautifulSoup
import time
import random
import re
import csv
import pandas as pd

KEY = 1  # 初次运行
MAX_MOVIES = 1000  # 最多爬取1000部电影

df = pd.read_csv('中国电影信息.csv')

if KEY == 1:
    y = 0
    anchor = 0
else:
    data = pd.read_csv("豆瓣电影信息.csv", header=None)
    data_1 = data.tail()
    col_1 = data_1[12]
    y = col_1.index.values[4] + 1
    z = []
    z.append(data_1.iat[4, 12])
    print('上次结束网址:', z[0])
    anchor = df[df['网址'].isin(z)].index.values[0] + 1

def get_ua():
    first_num = random.randint(55, 76)
    third_num = random.randint(0, 3800)
    fourth_num = random.randint(0, 140)
    os_type = [
        '(Windows NT 6.1; WOW64)', '(Windows NT 10.0; WOW64)', '(X11; Linux x86_64)',
        '(Macintosh; Intel Mac OS X 10_14_5)'
    ]
    chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num, fourth_num)

    ua = ' '.join(['Mozilla/5.0', random.choice(os_type), 'AppleWebKit/537.36',
                   '(KHTML, like Gecko)', chrome_version, 'Safari/537.36'])
    return ua

headers = {'User-Agent': get_ua()}
count = 0

with open('豆瓣电影信息.csv', 'a', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)

    for i in range(anchor, len(df)):
        if count >= MAX_MOVIES:
            print(f'已完成 {MAX_MOVIES} 部电影的爬取。')
            break

        url = df.iat[i, 0]
        print(f'正在爬取：{url}')
        headers_1 = {'User-Agent': get_ua()}

        try:
            response = requests.get(url=url, headers=headers_1, timeout=10)
            context = response.text
            bs_1 = BeautifulSoup(context, 'lxml')
            all_1 = bs_1.select('body>div>div>div>div>div>div>div>div')[1].text

            title = bs_1.select('body>div>div>h1>span')[0].text
            photo = bs_1.select('body>div>div>div>div>div>div>div>div>a>img')[0].get('src')
            brief = bs_1.select('body>div>div>div>div>div>div>span')[1].text.strip()

            def extract_value(keyword):
                if all_1.find(keyword) < 0:
                    return None
                start = all_1.find(keyword) + len(keyword)
                end = all_1.index('\n', start)
                return all_1[start:end].strip()

            director = extract_value('导演: ')
            actor = extract_value('主演:')
            type_ = extract_value('类型:')
            up_time = extract_value('上映日期:')

            if up_time:
                if ' / ' in up_time:
                    up_time = up_time.split(' / ')[0]
                if '-' not in up_time:
                    up_time = up_time[0:4]
                elif up_time.count('-') == 1:
                    up_time = up_time[0:7]
                elif up_time.count('-') == 2:
                    up_time = up_time[0:10]
                else:
                    up_time = None

            writer.writerow([title, director, actor, type_, brief, up_time, photo, url])
            count += 1
            print(f"第 {count} 部完成：{title}")
            print([title, type_, director, actor, brief, up_time, photo, url])

        except Exception as e:
            print(f"发生错误，跳过该链接：{url}，错误信息：{e}")
            time.sleep(2)
            continue
