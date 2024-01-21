from selenium.webdriver.chrome import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.support.wait import WebDriverWait


class BaseCrawler:
    driver: webdriver.WebDriver

    def __init__(self, headless: bool = True):
        self._init_driver(headless)

    def _init_driver(self, headless: bool = True):
        chrome_options = Options()
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36')
        if headless:
            chrome_options.add_argument("--headless")

            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-dev-shm-usage')

        self.driver = Chrome(options=chrome_options)

        # 注入js
        magic_js = open("./resource/p.js", "r").read()
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": magic_js
        })

        self.wait = WebDriverWait(self.driver, 30)

        # self.driver.maximize_window()
        self.driver.set_window_size(1920, 1080)
