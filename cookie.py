from core.xhs_crawler import XHSCrawler

if __name__ == '__main__':
    xhs_crawler = XHSCrawler("https://www.xiaohongshu.com/explore", "封开", headless=False)
    # xhs_crawler.save_cookies_manually()
    # xhs_crawler.do_login()
    # temp = xhs_crawler.get_page_info()
    xhs_crawler.obtain_cookie()