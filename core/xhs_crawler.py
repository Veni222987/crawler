import json
import os.path
import time
from time import sleep

from selenium.common import NoSuchElementException
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver import Keys
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from core.base_crawler import BaseCrawler
from core.cookie_pool import CookiePool


class XHSCrawler(BaseCrawler):
    cookie_pool: CookiePool
    cookies_path = "./cookies/xhs_cookies.json"
    driver: webdriver.WebDriver
    wait: WebDriverWait

    website = "xhs"

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
        "subtitles": '//*[@id="global"]/div[2]/div[2]/div/div[4]/div/div/div[2]',
        # //*[@id="global"]/div[2]/div[2]/div/div[4]/div/div/div[2]
        "qrcode": '//*[@id="qrcode"]/img',
        "login_btn": '//*[@id="login-btn"]/span',
        "user_profile": '//*[@id="global"]/div[2]/div[1]/ul/li[4]/div/a'
    }

    def __init__(self, url: str, keyword: str, pool: CookiePool, headless: bool = True):
        super().__init__(headless)
        self.url = url
        self.keyword = keyword
        self.cookie_pool = pool
        print('[Driver] init success')

    def check_login(self):
        self.driver.get(self.url)
        try:
            self.driver.find_element(By.XPATH, self.elements["qrcode"])
            return False
        except NoSuchElementException as e:
            return True

    def obtain_cookie(self):
        temp_url = "https://www.xiaohongshu.com/explore/6562b9ce000000003200ac22"
        self.driver.get(self.url)

        try:
            self.driver.find_element(By.XPATH, self.elements["qrcode"])
        except NoSuchElementException as e:
            # 尚未登录
            print("开始自旋等待登录")
            while True:
                try:
                    login_btn = self.driver.find_element(By.XPATH, self.elements["login_btn"])
                    time.sleep(1)
                    print("未登录成功")
                except NoSuchElementException as e:  # 直到登录按钮消失
                    break
            print("检测到登录成功")
            cookies = self.driver.get_cookies()
            try:
                user_ele = self.driver.find_element(By.XPATH, self.elements["user_profile"])
                user_id = user_ele.get_property("href").split("/")[-1]
            except Exception as e:
                ns = time.time_ns()
                print("获取user_id失败，随机生成：", ns)
                user_id = str(ns)
            self.cookie_pool.save_cookie(self.website, user_id, cookies)

    def do_login(self):
        temp_url = "https://www.xiaohongshu.com/explore/6562b9ce000000003200ac22"
        self.driver.get(self.url)
        while True:
            cookies = self.cookie_pool.get_rand_cookie(self.website)
            if len(cookies) == 0:
                print("cookie池为空，等待获取")  # TODO 短信/邮件通知
                sleep(3)
                continue
            else:
                break

        print("[Use Cookie]", cookies)
        for cookie in cookies:
            self.driver.add_cookie(cookie)

        # 尝试访问
        self.driver.get(temp_url)
        try:
            self.driver.find_element(By.XPATH, self.elements["qrcode"])
            raise Exception("账号登录失败")
        except NoSuchElementException as e:
            print("成功登录")

    def get_page_info(self) -> dict:
        res_dict = {}
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, self.elements["search_input"])))
            search_input = self.driver.find_element(By.XPATH, self.elements["search_input"])
            search_input.send_keys(self.keyword)
            search_input.send_keys(Keys.ENTER)
            print('[After Search Input] wait for 5s')
            sleep(5)
            actions = ActionChains(self.driver)
            actions.move_to_element(self.driver.find_element(By.XPATH, self.elements["dropdown_container"])).perform()
            sleep(1)
            hottest = self.driver.find_element(By.XPATH, self.elements["hottest"])
            hottest.click()
            print('[After Click Hot order] wait for 5s')
            sleep(5)

            subtitles = self.driver.find_element(By.XPATH, self.elements["subtitles"]).find_elements(By.XPATH,
                                                                                                     "./button")
            for subtitle in subtitles:
                try:
                    subtitle.click()
                    print(f'[After Click Subtitle] {subtitle.text}, wait for 5s')
                    sleep(5)
                    notes_div = self.driver.find_element(By.XPATH, self.elements["notes_div"])
                    continue_flag = True
                    while continue_flag:
                        # 模拟滚轮向下
                        print(f'[Scroll Down] notes count: {len(res_dict)}')
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
                                else:
                                    continue_flag = False
                            except Exception as e:
                                print("爬取单篇笔记失败", e.args)
                                continue
                except Exception as e:
                    print("爬取单个subtitle失败")
                    print(e)
                    continue
        except Exception as e:
            print("获取关键词信息失败")
            print(e)
            self.driver.save_screenshot("./获取关键词信息.png")
            return res_dict

        return res_dict

    def save_data(self, data: dict, keyword: str):
        try:
            if not os.path.exists("./output"):
                os.makedirs("./output")
            with open("./output/" + keyword + ".json", "w", encoding="utf-8") as f:
                f.truncate()
                json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            print("保存文件失败")
            print(e)

# if __name__ == '__main__':
#     xhs_crawler = XHSCrawler("https://www.xiaohongshu.com/explore", "封开")
#     # xhs_crawler.save_cookies_manually()
#     xhs_crawler.do_login()
#     temp = xhs_crawler.get_page_info()
#     xhs_crawler.save_data(temp, xhs_crawler.keyword)
