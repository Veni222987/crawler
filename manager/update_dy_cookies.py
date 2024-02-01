from core.cookie_pool import CookiePool
from core.dy_crawler import DyCrawler

dy_crawler = DyCrawler("https://www.douyin.com/discover", "LEGO",
                         pool=CookiePool(host="43.139.80.71", port=6378, db=3, password="dsfkjojo432rn5"),
                         headless=False)
dy_crawler.obtain_cookie()