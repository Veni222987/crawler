from core.cookie_pool import CookiePool
from core.xhs_crawler import XHSCrawler

xhs_crawler = XHSCrawler("https://www.xiaohongshu.com/explore", "LEGO",
                         pool=CookiePool(host="43.139.80.71", port=6378, db=3, password="dsfkjojo432rn5"),
                         headless=False)
xhs_crawler.obtain_cookie()
