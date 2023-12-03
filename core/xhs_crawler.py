import json
import os.path
from time import sleep

from selenium.webdriver import Chrome
from selenium.webdriver import Keys
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class XHSCrawler:
    driver: webdriver.WebDriver
    wait: WebDriverWait
    url: str
    keyword: str
    elements = {
        "search_input": '//*[@id="global"]/div[1]/header/div[2]/input',
        "notes_div": '//*[@id="global"]/div[2]/div[2]/div/div[4]',
        "title": '//*[@id="global"]/div[2]/div[2]/div/div[4]/section[1]/div/div/a/span',
        "like_count": '//*[@id="global"]/div[2]/div[2]/div/div[4]/section[1]/div/div/div/span/span[2]',
        "author": '//*[@id="global"]/div[2]/div[2]/div/div[4]/section[1]/div/div/div/a/span',
        "url": '//*[@id="global"]/div[2]/div[2]/div/div[4]/section[1]/div/a[1]'
    }

    def __init__(self, url: str, keyword: str):
        self.url = url
        self.keyword = keyword
        self._init_driver()

    # 初始化driver 和 wait
    def _init_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36')

        self.driver = Chrome(options=chrome_options)
        with open('../resource/p.js') as f:
            js = f.read()

        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": js
        })

        self.wait = WebDriverWait(self.driver, 30)

    def save_cookies_manually(self):
        self.driver.get(self.url)
        while 1:
            cookies = self.driver.get_cookies()
            print(cookies)
            with open("./xhs_crawler_cookies.json", "w") as f:
                f.truncate()
                json.dump(cookies, f)

    def do_login(self):
        temp_url = "https://www.xiaohongshu.com/explore/6562b9ce000000003200ac22"
        self.driver.get(self.url)
        sleep(3)
        # 获取cookies，此处实现为本地获取，也可实现为redis获取
        if os.path.exists("./xhs_crawler_cookies.json"):
            with open("./xhs_crawler_cookies.json", "r") as f:
                cookies = json.load(f)
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        self.driver.refresh()
        print(self.driver.get_cookies())
        sleep(3)

    def get_page_info(self) -> list:
        res_list = []

        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, self.elements["search_input"])))
            search_input = self.driver.find_element(By.XPATH, self.elements["search_input"])
            search_input.send_keys(self.keyword)
            search_input.send_keys(Keys.ENTER)
            sleep(5)
            notes_div = self.driver.find_element(By.XPATH, self.elements["notes_div"])
            notes = notes_div.find_elements(By.XPATH, "./section")
            sleep(5)
            for note in notes:
                try:
                    title = note.find_element(By.XPATH, "./div/div/a/span").text
                    like_count = note.find_element(By.XPATH, "./div/div/div/span/span[2]").text
                    author = note.find_element(By.XPATH, "./div/div/div/a/span").text
                    url = note.find_element(By.XPATH, "./div/a[1]").get_attribute("href")
                    res_list.append({
                        "title": title,
                        "like_count": like_count,
                        "author": author,
                        "url": url
                    })
                    print(title, like_count, author, url)
                except Exception as e:
                    print(e)
                    continue
        except Exception as e:
            print(e)
            return res_list

        return res_list

    def save_data(self, data: list):
        with open("../output/" + self.keyword + ".json", "w", encoding="utf-8") as f:
            f.truncate()
            json.dump(data, f, ensure_ascii=False)


if __name__ == '__main__':
    xhs_crawler = XHSCrawler("https://www.xiaohongshu.com/explore", "深圳")
    # xhs_crawler.save_cookies_manually()
    xhs_crawler.do_login()
    temp = xhs_crawler.get_page_info()
    xhs_crawler.save_data(temp)
