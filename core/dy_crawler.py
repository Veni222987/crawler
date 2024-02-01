import time

from selenium.common import NoSuchElementException
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
        time.sleep(3)
        try:
            self.driver.find_element(By.XPATH, self.elements['qrcode'])
            raise Exception("账号登录失败")
        except NoSuchElementException:
            print("登录成功")
