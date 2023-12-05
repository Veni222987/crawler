import json
import os.path
from time import sleep

from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver import Keys
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class XHSCrawler:
    cookies_path = "./cookies/xhs_cookies.json"
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
        "url": '//*[@id="global"]/div[2]/div[2]/div/div[4]/section[1]/div/a[1]',
        "hottest": '/html/body/div[4]/div/li[3]',
        "dropdown_container": '//*[@id="global"]/div[2]/div[2]/div/div[1]/div[2]/div',
        "subtitles": '//*[@id="global"]/div[2]/div[2]/div/div[3]/div/div/div[2]'
    }

    def __init__(self, url: str, keyword: str):
        self.url = url
        self.keyword = keyword
        self._init_driver()

    # 初始化driver 和 wait
    def _init_driver(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument(
        #     'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36')
        #
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = Chrome(options=chrome_options)

        # 注入js
        magic_js = open("./resource/p.js", "r").read()
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": magic_js
        })

        self.wait = WebDriverWait(self.driver, 30)

    def save_cookies_manually(self):
        self.driver.get(self.url)
        if not os.path.exists("./cookies"):
            os.makedirs("./cookies")
        while 1:
            cookies = self.driver.get_cookies()
            print(cookies)
            # 目录不存在则创建
            with open(self.cookies_path, "w") as f:
                f.truncate()
                json.dump(cookies, f)

    def do_login(self):
        temp_url = "https://www.xiaohongshu.com/explore/6562b9ce000000003200ac22"
        self.driver.get(self.url)
        sleep(3)
        # 获取cookies，此处实现为本地获取，也可实现为redis获取
        if os.path.exists(self.cookies_path):
            with open(self.cookies_path, "r") as f:
                cookies = json.load(f)
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        self.driver.refresh()
        print(self.driver.get_cookies())
        sleep(3)
        with open(self.cookies_path, "w") as f:
            f.truncate()
            json.dump(self.driver.get_cookies(), f)

    def get_page_info(self) -> dict:
        res_dict = {}
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, self.elements["search_input"])))
            search_input = self.driver.find_element(By.XPATH, self.elements["search_input"])
            search_input.send_keys(self.keyword)
            search_input.send_keys(Keys.ENTER)
            sleep(5)
            actions = ActionChains(self.driver)
            actions.move_to_element(self.driver.find_element(By.XPATH, self.elements["dropdown_container"])).perform()
            sleep(1)
            hottest = self.driver.find_element(By.XPATH, self.elements["hottest"])
            hottest.click()
            sleep(5)
            subtitles = self.driver.find_element(By.XPATH, self.elements["subtitles"]).find_elements(By.XPATH,
                                                                                                     "./button")
            for subtitle in subtitles:
                try:
                    subtitle.click()
                    sleep(5)
                    notes_div = self.driver.find_element(By.XPATH, self.elements["notes_div"])
                    continue_flag = True
                    while continue_flag:
                        # 模拟滚轮向下
                        self.driver.execute_script(f"window.scrollBy(0, 300);")
                        sleep(3)
                        notes = notes_div.find_elements(By.XPATH, "./section")
                        for note in notes:
                            try:
                                title = note.find_element(By.XPATH, "./div/div/a/span").text
                                like_count = note.find_element(By.XPATH, "./div/div/div/span/span[2]").text
                                author = note.find_element(By.XPATH, "./div/div/div/a/span").text
                                url = note.find_element(By.XPATH, "./div/a[1]").get_attribute("href")
                                note_id = url.split("/")[-1]
                                if int(like_count) > 30:
                                    temp_note = {
                                        "title": title,
                                        "like_count": like_count,
                                        "author": author,
                                        "url": url,
                                        "subtitle": subtitle.text,
                                    }
                                    # 如果笔记存在全局字典中，拼接subtitle
                                    if note_id in res_dict and res_dict[note_id]["subtitle"].split(',')[-1] != \
                                            temp_note[
                                                "subtitle"]:
                                        temp_note["subtitle"] = res_dict[note_id]["subtitle"] + "," + temp_note[
                                            "subtitle"]
                                    res_dict[note_id] = temp_note
                                    print(temp_note)
                                else:
                                    continue_flag = False
                            except Exception as e:
                                print("爬取单篇笔记失败")
                                print(e)
                                continue
                except Exception as e:
                    print("爬取单个subtitle失败")
                    print(e)
                    continue
        except Exception as e:
            print("获取关键词信息失败")
            print(e)
            return res_dict

        return res_dict

    def save_data(self, data: dict, file_name: str):
        try:
            if not os.path.exists("./output"):
                os.makedirs("./output")
            with open("./output/" + file_name + ".json", "w", encoding="utf-8") as f:
                f.truncate()
                json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            print("保存文件失败")
            print(e)


if __name__ == '__main__':
    xhs_crawler = XHSCrawler("https://www.xiaohongshu.com/explore", "封开")
    # xhs_crawler.save_cookies_manually()
    xhs_crawler.do_login()
    temp = xhs_crawler.get_page_info()
    xhs_crawler.save_data(temp, xhs_crawler.keyword)
