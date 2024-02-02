import time

from async_schedule.op import TaskOperator
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from config.config_loader import loader
from core.base_crawler import BaseCrawler
from core.cookie_pool import CookiePool
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class DyCrawler(BaseCrawler):
    cookie_pool: CookiePool
    cookies_path = "./cookies/dy_cookies.json"
    driver: webdriver.WebDriver
    wait: WebDriverWait
    website = "dy"
    elements = {}

    url: str
    keyword: str

    def __init__(self, url: str, keyword: str, pool: CookiePool, headless: bool = True):
        super().__init__(headless)
        self.url = url
        self.keyword = keyword
        self.cookie_pool = pool
        self._get_elements()
        print('[Driver] init success')

    def _get_elements(self):
        self.elements = loader.load_all(self.website).page_elements

    def check_login(self):
        self.driver.get(self.url)
        try:
            self.driver.find_element(By.XPATH, self.elements["qrcode"])
            return False
        except NoSuchElementException:
            return True

    def obtain_cookie(self):
        self.driver.get(self.url)
        time.sleep(5)
        while True:
            try:
                self.driver.find_element(By.XPATH, self.elements['qrcode'])
                time.sleep(5)
            except NoSuchElementException:
                break

        print('检测到登陆成功')
        cookies = self.driver.get_cookies()

        # 尝试获取id
        try:
            # self.driver.find_element(By.XPATH, self.elements['mine']).click()
            # time.sleep(3)
            self.driver.get('https://www.douyin.com/user/self')
            time.sleep(3)
            user_id = self.driver.find_element(By.XPATH, self.elements['user_id']).text
        except NoSuchElementException:
            ns = time.time_ns()
            print("获取user_id失败，随机生成：", ns)
            user_id = str(ns)

        self.cookie_pool.save_cookie(self.website, user_id, cookies)

    def do_login(self):
        self.driver.get(self.url)
        while True:
            cookies = self.cookie_pool.get_rand_cookie(self.website)
            if len(cookies) == 0:
                print("cookie池为空，等待获取")
                # [TODO] 发送邮件通知管理员
                time.sleep(5)
                continue
            else:
                break

        print("[Use Cookie]", cookies)
        for cookie in cookies:
            self.driver.add_cookie(cookie)

        self.driver.get(self.url)
        time.sleep(5)
        try:
            self.driver.find_element(By.XPATH, self.elements['qrcode'])
            raise Exception("账号登录失败")
        except NoSuchElementException:
            print("登录成功")

    def get_page_info(self, op: TaskOperator) -> dict:
        res_dict: dict = {}
        try:
            # 输入框输入关键字
            search_input = self.driver.find_element(By.XPATH, self.elements['search_input'])
            search_input.send_keys(self.keyword)
            search_input.send_keys(Keys.ENTER)
            print('[After Search Input] wait for 5s')
            time.sleep(5)
            # 切换到新窗口
            new_window = self.driver.window_handles[1]
            self.driver.switch_to.window(new_window)
            time.sleep(5)
            # 点击视频选项
            self.driver.find_element(By.XPATH, self.elements['video_btn']).click()
            time.sleep(5)
            # [TODO] 切换排序到最热，隐藏元素找不出来
            # self.driver.find_element(By.XPATH.self.elements['drop_down']).click()
            # time.sleep(1)
            # self.driver.find_element(By.XPATH,self.elements['hottest']).click()
            # 爬取子标题
            subtitles = []
            try:
                subtitles_bar = self.driver.find_element(By.XPATH, self.elements['subtitles_bar'])
                subtitles = subtitles_bar.find_elements(By.XPATH, './div')
            except NoSuchElementException:
                self._get_subtitle_notes(0, res_dict, None, op)
            for subtitle in subtitles:
                try:
                    subtitle.click()
                    print('开始爬取子标题', subtitle.text)
                    time.sleep(5)
                    self._get_subtitle_notes(100, res_dict, subtitle, op)
                except Exception:
                    try:
                        self.driver.find_element(By.XPATH, self.elements['subtitles_scroller']).click()
                        print("[Click Subtitles Scroller]点击子标题滚动成功")
                        self._get_subtitle_notes(100, res_dict, subtitle, op)
                    except Exception as e:
                        print("[Click Subtitles Scroller]点击子标题滚动失败")
                        print(e)
        except Exception as e:
            print('获取关键词信息失败')
            print(e)
            self.driver.save_screenshot("./output/dy获取关键词信息.png")
            return res_dict

        return res_dict

    def _get_subtitle_notes(self, deadline: 30, res_dict: dict, subtitle, op: TaskOperator):
        # 抖音的滚动处理策略是一直添加li选项，遍历笔记处理和小红书不同
        notes_div = self.driver.find_element(By.XPATH, self.elements['notes_div'])
        continue_flag = True
        index = 1
        counter = 0
        while continue_flag:
            previous_notes = len(res_dict)
            length = len(notes_div.find_elements(By.XPATH, './li'))
            while index <= length:
                # 获取index的笔记
                # 点赞数: /li[1]/div/a/div/div[1]/div/div[2]/div[2]/div[3]/span
                # 标题： /li[1]/div/a/div/div[2]/div/div[1]
                # 作者： /li[1]/div/a/div/div[2]/div/div[2]/span[1]/span[2]
                # url： /li[1]/div/a
                try:
                    note = notes_div.find_element(By.XPATH, './li[{}]/div'.format(index))
                    like_count = note.find_element(By.XPATH, './a/div/div[1]/div/div[2]/div[2]/div[3]/span').text
                    if like_count[-1] == '万':
                        like_count = int(float(like_count[:-1]) * 10000)
                    url = note.find_element(By.XPATH, './a').get_attribute("href")
                    note_id = url.split("/")[-1]
                    if int(like_count) > deadline and counter < 10:
                        temp_video = {
                            "url": url,
                            'subtitle': subtitle.text if not subtitle is None else '综合',
                            'like_count': like_count,
                            'title': note.find_element(By.XPATH, './a/div/div[2]/div/div[1]').text,
                            'author': note.find_element(By.XPATH, './a/div/div[2]/div/div[2]/span[1]/span[2]').text
                        }
                        if not subtitle is None:
                            if note_id in res_dict and res_dict[note_id]["subtitle"].split(',')[-1] != temp_video[
                                "subtitle"]:
                                temp_video["subtitle"] = res_dict[note_id]["subtitle"] + "," + temp_video["subtitle"]
                            res_dict[note_id] = temp_video
                        else:
                            res_dict[note_id] = temp_video

                    else:
                        continue_flag = False
                        counter = 0
                except Exception as e:
                    print("爬取某个视频失败", e)

                print('[notes count]', len(res_dict))
                index = index + 1

            # 模拟鼠标滚轮向下：
            print(f'[Scroll Down] notes count: {len(res_dict)}')

            self.driver.execute_script(f"window.scrollBy(0, 500);")
            time.sleep(0.5)

            # 结束条件
            if len(res_dict) == previous_notes:
                counter = counter + 1
            if counter > 10:
                continue_flag = False
