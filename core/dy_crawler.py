from core.base_crawler import BaseCrawler
from core.cookie_pool import CookiePool


class DyCrawler(BaseCrawler):


    def __init__(self, url: str, keyword: str, pool: CookiePool, headless: bool = True):
        super().__init__(headless)
        self.url = url
        self.keyword = keyword
        self.cookie_pool = pool
        print('[Driver] init success')
    def check_login(self):
        self.driver.get(self.url)
