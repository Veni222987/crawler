import json
import time

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

if __name__ == '__main__':
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36')

    driver = Chrome(options=chrome_options)
    with open('core/p.js') as f:
        js = f.read()

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": js
    })
    # -------------------------------------------------------------------------------------------------
    # driver.get("https://www.xiaohongshu.com/explore")
    # while (1):
    #     cookies = driver.get_cookies()
    #     if len(cookies) > 0:
    #         print(cookies)
    #         with open("./xhs_crawler_cookies.json", "w") as f:
    #             f.truncate()
    #             json.dump(cookies, f)
    # -------------------------------------------------------------------------------------------------
    driver.get("https://xiaohongshu.com/explore")
    with open("./xhs_crawler_cookies.json", "r") as f:
        cookies = json.load(f)
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    time.sleep(50000)
