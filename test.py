from async_schedule.op import TaskOperator

from core.cookie_pool import CookiePool
from core.xhs_crawler import XHSCrawler


xhs_crawler = XHSCrawler("https://www.xiaohongshu.com/explore", "IRY",
                         pool=CookiePool(host="43.139.80.71", port=6378, db=3, password="dsfkjojo432rn5"),
                         headless=True)
xhs_crawler.do_login()
op=TaskOperator
dict = xhs_crawler.get_page_info(op)
