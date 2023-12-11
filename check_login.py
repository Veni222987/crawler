import time

from core.cookie_pool import CookiePool
from core.xhs_crawler import XHSCrawler

if __name__ == '__main__':
    xhs_crawler = XHSCrawler("https://www.xiaohongshu.com/explore", "封开",
                             pool=CookiePool(host="43.139.80.71", port=6378, db=3, password="dsfkjojo432rn5"),
                             headless=False)

    xhs_crawler.do_login()
    xhs_crawler.check_login()
    time.sleep(500)
