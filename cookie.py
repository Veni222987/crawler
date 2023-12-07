from core.cookie_pool import CookiePool
from core.xhs_crawler import XHSCrawler

if __name__ == '__main__':
    xhs_crawler = XHSCrawler("https://www.xiaohongshu.com/explore", "封开",
                             pool=CookiePool(host="43.139.80.71", port=6378, db=3, password="dsfkjojo432rn5"),
                             headless=False)
    # xhs_crawler.save_cookies_manually()
    # xhs_crawler.do_login()
    # temp = xhs_crawler.get_page_info()
    xhs_crawler.obtain_cookie()
