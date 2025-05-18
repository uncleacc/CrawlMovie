from selenium import webdriver
import time
import  xlwt
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
savepath="详情页网址.xls"
'''#无UI环境调试
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
# path是你自己的chrome浏览器的文件路径
path = r'C:\SUN\AppData\Local\Google\Chrome\Application\chrome.exe'  #这个是软件chrome.exe的安装路径
browser = webdriver.Chrome(chrome_options=chrome_options)
'''


#  有ui情况(打开无ui后，这两行要注释掉
path = 'chromedriver.exe'
browser = webdriver.Chrome(path)

#对网址进行访问
url ='https://movie.douban.com/explore'
browser.get(url)
time.sleep(2)
n=0  #地区循环数
y=1  #记录爬取条数
#对存入表格进行初始化
book = xlwt.Workbook(encoding="utf-8", style_compression=0)    #定义格式
sheet = book.add_sheet('详情页网址', cell_overwrite_ok=True)    #定义内页名
sheet.write(0, 0,'网址')  #存入表头



while n<20:     #地区循环
    m = 0  # 年代循环数
    while m<13:   #年代循环
        #横表头五个
        if n==0 and m==0:  #第一次循环开始初始状态
            #butten_main是五个主标签的获取
            #butten_main = browser.find_elements_by_class_name('base-selector-title')
            butten_main = browser.find_elements('base-selector-title')
            butten_main[1].click()
            time.sleep(1)
            # butten_place是地址副标签的获取
            #butten_place = browser.find_elements_by_class_name('tag-group-item')
            butten_place = browser.find_elements('tag-group-item')
            time.sleep(1)
            #butten_place[3].click()    #从韩国开始
            butten_place[14].click()  #从印度开始
            #butten_main = browser.find_elements_by_class_name('base-selector-title')
            butten_main = browser.find_elements('base-selector-title')
            butten_main[2].click()
            time.sleep(1)
            #butten_time是时代副标签的获取
            #butten_time = browser.find_elements_by_class_name('tag-group-item')
            butten_time = browser.find_elements('tag-group-item')
            butten_time[2].click()
            #time.sleep(1)
        else:   #非起始状态，每次只用找到并改变时间的副标签
            #butten_main = browser.find_elements_by_class_name('base-selector-title')
            butten_main = browser.find_elements('base-selector-title')
            butten_main[2].click()
            time.sleep(1)
           # butten_time = browser.find_elements_by_class_name('tag-group-item')
            butten_time = browser.find_elements('tag-group-item')
            butten_time[m+2].click()
            time.sleep(2)
        m=m+1
        x = 0  # 单页刷新数
        while x<28:#每确定一页都要刷到最底端
            time.sleep(1)
            #下拉页面
            js = "window.scrollTo(0,document.body.scrollHeight)"
            browser.execute_script(js)
            time.sleep(2)
            #butten_more = browser.find_elements_by_class_name('explore-more')
            butten_more = browser.find_elements('explore-more')
            if len(butten_more)==1:#用于辨识是否还能刷新出来，防止电影不多的情况
                butten_more[0].click()
            else:
                x=100     #若不能加载更多，则跳出循环
            time.sleep(2)
            x=x+1
        #对每页进行处理
        content = browser.page_source
        soup = BeautifulSoup(content, "html.parser")
        movie_li = soup.select('body>div>div>div>div>div>div>div>ul>li')
        print(len(movie_li))
        for movie_li_one in movie_li:
            li = movie_li_one.select('li>a')
            value = li[0].get('href')  #获取网址
            #sheet.write(y,0,y)         #写入个数
            sheet.write(y, 0, value)    #写入网址
            book.save(savepath)         #进行储存
            print(value,'第',y,'条')
            y=y+1

    #butten_two为地区被选择时，寻找地区主标签使用
   # butten_two = browser.find_elements_by_class_name('base-selector-selected')
    butten_two = browser.find_elements('base-selector-selected')
    butten_two[0].click()
    time.sleep(1)
    #butten_place = browser.find_elements_by_class_name('tag-group-item')
    butten_place = browser.find_elements('tag-group-item')
    butten_place[n + 4].click()#重要的更改位置！！！！！！！！！！！！
    #因xls文件最大只能容纳65555条数据，当爬取的一定程度文件会被填满，无法写入，
    #这时候就要停止（手动检查并停止运行）爬取！更改butten_place[n + 4].click()
    # 中的4使其从上次运行中断位置开始，这个只能修改大致的范围，不能接确到确定的网址！

    time.sleep(1)
    n=n+1