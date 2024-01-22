import json
import os.path
import time
from time import sleep

from async_schedule.op import TaskOperator
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver import Keys
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from config.config_loader import loader
from core.base_crawler import BaseCrawler
from core.cookie_pool import CookiePool
from utils.email_util import EmailUtil


class XHSCrawler(BaseCrawler):
    cookie_pool: CookiePool
    cookies_path = "./cookies/xhs_cookies.json"
    driver: webdriver.WebDriver
    wait: WebDriverWait
    website = "xhs"
    elements = {}

    url: str
    keyword: str

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
        self._get_elements()
        temp_url = "https://www.xiaohongshu.com/explore/6562b9ce000000003200ac22"
        self.driver.get(self.url)
        while True:
            cookies = self.cookie_pool.get_rand_cookie(self.website)
            if len(cookies) == 0:
                print("cookie池为空，等待获取")  # 短信/邮件通知
                # EmailUtil.send_email(['1948160779@qq.com'], 'cookie池为空', '请维护cookie池')
                sleep(3)
                continue
            else:
                break

        print("[Use Cookie]", cookies)
        for cookie in cookies:
            self.driver.add_cookie(cookie)

        # 尝试访问
        self.driver.get(temp_url)
        sleep(1)
        try:
            self.driver.find_element(By.XPATH, self.elements["login_btn"])
            # EmailUtil.send_email(['1948160779@qq.com'], 'cookie失效', '请维护cookie池')
            raise Exception("账号登录失败")
        except NoSuchElementException as e:
            print("成功登录")

    def _get_all_notes(self, deadline: 30, res_dict: dict, subtitle, op: TaskOperator):
        notes_div = self.driver.find_element(By.XPATH, self.elements["notes_div"])
        continue_flag = True
        counter = 0

        while continue_flag:
            # 模拟滚轮向下
            print(f'[Scroll Down] notes count: {len(res_dict)}')
            previous_len = len(res_dict)
            self.driver.execute_script(f"window.scrollBy(0, 500);")
            sleep(0.5)
            notes = notes_div.find_elements(By.XPATH, "./section")
            for note in notes:
                try:
                    like_count = note.find_element(By.XPATH, "./div/div/div/span/span[2]").text
                    url = note.find_element(By.XPATH, "./div/a[1]").get_attribute("href")
                    note_id = url.split("/")[-1]
                    if like_count[-1] == "w":
                        like_count = str(int(float(like_count[:-1]) * 10000))
                    if int(like_count) > deadline and counter < 10:
                        temp_note = {
                            "url": url,
                            "subtitle": subtitle.text if not subtitle is None else "",
                            "like_count": like_count,
                            "title": note.find_element(By.XPATH, "./div/div/a/span").text,
                            "author": note.find_element(By.XPATH, "./div/div/div/a/span").text,
                        }

                        # subtitle非空时执行
                        if not subtitle is None:
                            # 如果笔记存在全局字典中，拼接subtitle
                            if note_id in res_dict and res_dict[note_id]["subtitle"].split(',')[-1] != temp_note[
                                "subtitle"]:
                                temp_note["subtitle"] = res_dict[note_id]["subtitle"] + "," + temp_note["subtitle"]
                            res_dict[note_id] = temp_note
                        else:
                            res_dict[note_id] = temp_note
                    else:
                        continue_flag = False
                        counter = 0
                except Exception as e:
                    print("爬取单篇笔记失败", e.args)
                    continue

            if len(res_dict) == previous_len:
                counter = counter + 1
            else:
                counter = 0
            # self.save_progress(op, counter)

    def get_page_info(self, op: TaskOperator) -> dict:
        self._get_elements()
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

            # 检测subtitle存在性，没有就直接跳
            subtitles = []
            try:
                # 等待页面加载完成
                subtitles_bar = self.driver.find_element(By.XPATH, self.elements["subtitles"])
                subtitles = subtitles_bar.find_elements(By.XPATH,".//button")
            except NoSuchElementException as e:
                self._get_all_notes(0, res_dict, None, op)
            for subtitle in subtitles:
                while True:
                    try:
                        subtitle.click()
                        print("开始爬取子标题：", subtitle.text)
                        sleep(5)
                        self._get_all_notes(50, res_dict, subtitle, op)
                        break
                    except Exception as e:
                        try:
                            self.driver.find_element(By.XPATH, self.elements['subtitles_scroller']).click()
                            print("[Click Subtitles Scroller]点击子标题滚动成功")
                        except Exception as e:
                            print("[Click Subtitles Scroller]点击子标题滚动失败")
                            print(e)
                # try:
                #     while not subtitle.is_enabled():
                #         try:
                #             self.driver.find_element(By.XPATH, self.elements['subtitles_scroller']).click()
                #             print("[Click Subtitles Scroller]点击子标题滚动成功")
                #         except Exception as e:
                #             print("[Click Subtitles Scroller]点击子标题滚动失败")
                #             print(e)
                #     subtitle.click()
                #
                #     print(f'[After Click Subtitle] {subtitle.text}, wait for 5s')
                #     sleep(5)
                #
                # except Exception as e:
                #     print("爬取单个subtitle失败")
                #     print(e)
                #     continue
        except Exception as e:
            print("获取关键词信息失败")
            print(e)
            self.driver.save_screenshot("./output/获取关键词信息.png")
            return res_dict

        return res_dict

    def save_progress(self, op: TaskOperator, hasGot: int):
        got = f"got={hasGot}"
        op.set_stage(got)

    @staticmethod
    def parse_progress(text: str) -> int:
        if text == "":
            return 0
        return int(text.split("=")[-1])

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

    def _get_elements(self):
        self.elements = loader.load_all().page_elements
