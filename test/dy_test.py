from async_schedule.op import TaskOperator

from core.cookie_pool import CookiePool
from core.dy_crawler import DyCrawler

dy_crawler = DyCrawler("https://www.douyin.com/discover", "IRY",
                       pool=CookiePool(host="43.139.80.71", port=6378, db=3, password="dsfkjojo432rn5"),
                       headless=False)
dy_crawler.do_login()
op=TaskOperator
dict = dy_crawler.get_page_info(op)
print(dict)