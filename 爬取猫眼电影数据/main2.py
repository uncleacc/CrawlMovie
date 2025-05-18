import csv
import random
import time
import json
import redis

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DIRVER_PATH = r'chromedriver.exe'
# 跳过selenium检测
STEALTH_JS = r'stealth.min.js'
# Redis配置
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_KEY = 'maoyan_crawler_state'

path_map = {
    '电影名称': '//h1[@class="name"]',
    '导演': '//div[@class="celebrity-group"]/ul/li[@class="celebrity "]/div[@class="info"]/div[@class="name"]',
    '类型': '//li[@class="ellipsis"][1]',
    '上映时间': '//li[@class="ellipsis"][3]',
    '简介': '//div[@class="tab-desc tab-content active"]/div/div[@class="mod-content"]/span[@class="dra"]',
    '头图': '//img[@class="avatar"]'
}


def get_element(elem_name, driver):
    # 提取上映时间
    try:
        release_date_element = driver.find_element(By.XPATH, path_map[elem_name])
        if elem_name == '头图':
            return release_date_element.get_attribute('src')
        return release_date_element.text
    except NoSuchElementException:
        print('提取元素失败: %s' % elem_name)
        return "未公布"


def save_state(redis_client, current_page, current_index, total_count):
    """保存爬虫状态到Redis"""
    state = {
        'current_page': current_page,
        'current_index': current_index,
        'total_count': total_count
    }
    redis_client.set(REDIS_KEY, json.dumps(state))


def load_state(redis_client):
    """从Redis加载爬虫状态"""
    state = redis_client.get(REDIS_KEY)
    if state:
        return json.loads(state)
    return {'current_page': 1, 'current_index': 0, 'total_count': 0}


def main():
    # 连接Redis
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    # 加载状态
    state = load_state(redis_client)
    current_page = state['current_page']
    current_index = state['current_index']
    total_count = state['total_count']

    print(f"从第{current_page}页，第{current_index}个电影开始爬取，已爬取{total_count}部电影")

    service = ChromeService(executable_path=DIRVER_PATH)

    options = webdriver.ChromeOptions()

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # 不退出浏览器
    # options.add_experimental_option('detach', True)

    # 防止检测到selenium
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=service, options=options)

    with open(STEALTH_JS) as f:
        js = f.read()

    driver.execute_cdp_cmd(
        cmd="Page.addScriptToEvaluateOnNewDocument",
        cmd_args={
            "source": js
        }
    )

    # 打开一个标签页
    driver.get("https://www.maoyan.com/films?showType=3")

    # 最大化
    driver.maximize_window()

    # 隐式等待最长时间：5秒
    driver.implicitly_wait(5)

    # 导航到保存的页面
    for _ in range(current_page - 1):
        try:
            next_page_ele = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "下一页"))
            )
            next_page_ele.click()
            print(f"导航到第{current_page}页")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'movies-list'))
            )
        except Exception as e:
            print(f"导航到第{current_page}页失败: {e}")
            return

    with open('猫眼电影信息.csv', 'a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)

        # 如果是新爬取或第一页，写入表头
        if current_page == 1 and current_index == 0:
            writer.writerow(['电影名称', '类型', '导演', '演员', '上映时间', '简介', '头图'])

        while True:
            try:
                next_page_ele = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "下一页"))
                )
            except:
                print("没有下一页了，爬取完成")
                break

            elements = driver.find_elements(By.XPATH,
                                            '//div[@class="movies-list"]/dl/dd/div[@class="movie-item film-channel"]')

            # 如果是当前页，跳过已经爬取的电影
            if current_index > 0:
                elements = elements[current_index:]
                current_index = 0

            for index, element in enumerate(elements, 1):
                try:
                    ActionChains(driver).move_to_element(element).click().perform()

                    print("切换到最后的标签页")
                    print(driver.current_url)
                    driver.switch_to.window(driver.window_handles[-1])

                    # 等待详情页加载
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'movie-brief-container'))
                    )

                    movies_data = {}

                    movies_data['电影名称'] = get_element('电影名称', driver)
                    movies_data['类型'] = get_element('类型', driver)
                    movies_data['导演'] = get_element('导演', driver)
                    elements = driver.find_elements(By.XPATH, '//div[@class="celebrity-group"]/ul/li[@class="celebrity actor"]/div[@class="info"]/div[@class="name"]')
                    movies_data['演员'] = ' '.join([element.text for element in elements])
                    # movies_data['演员'] = driver.find_elements(By.XPATH, '//div[@class="celebrity-group"]/ul/li[@class="celebrity actor"]/div[@class="info"]/div[@class="name"]')
                    movies_data['上映时间'] = get_element('上映时间', driver)
                    movies_data['简介'] = get_element('简介', driver)
                    movies_data['头图'] = get_element('头图', driver)

                    print(movies_data.values())

                    total_count += 1
                    print("第%d部电影数据爬取完成" % total_count)

                    # 写入数据
                    writer.writerow(movies_data.values())

                    # 保存状态
                    save_state(redis_client, current_page, index, total_count)

                    if total_count == 1000:
                        print("已完成1000部电影数据的爬取")
                        redis_client.delete(REDIS_KEY)  # 爬取完成，删除状态
                        driver.quit()
                        return

                    # 关闭标签页
                    driver.close()
                    # 回到原来的页面
                    driver.switch_to.window(driver.window_handles[0])
                    # 休息一下
                    # time.sleep(random.randint(1, 3))
                except Exception as e:
                    print(f"爬取第{index}个电影出错: {e}")
                    # 关闭标签页
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    # 保存当前状态
                    save_state(redis_client, current_page, index, total_count)
                    # time.sleep(5)  # 出错后多休息一会

            print("点击下一页")
            current_page += 1
            current_index = 0
            try:
                next_page_ele.click()
                # 保存翻页状态
                save_state(redis_client, current_page, current_index, total_count)
                # 等待页面加载
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'movies-list'))
                )
                time.sleep(1)  # 页面加载后等待一下
            except Exception as e:
                print(f"点击下一页失败: {e}")
                break

    redis_client.delete(REDIS_KEY)  # 爬取完成，删除状态
    time.sleep(10)
    driver.quit()


if __name__ == '__main__':
    main()