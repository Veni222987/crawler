import json

import consul

from core.cookie_pool import CookiePool
from core.xhs_crawler import XHSCrawler
from utils.email_util import EmailUtil

elements = {
    "search_input": '//*[@id="global"]/div[1]/header/div[2]/input',
    "notes_div": '//*[@id="global"]/div[2]/div[2]/div/div[last()-1]',
    # 有品牌有子标题，WIS             '//*[@id="global"]/div[2]/div[2]/div/div[5]'
    # 无品牌有子标题，广州             '//*[@id="global"]/div[2]/div[2]/div/div[4]'
    # 无品牌无子标题，ssss            '//*[@id="global"]/div[2]/div[2]/div/div[3]'
    "title": '//*[@id="global"]/div[2]/div[2]/div/div[4]/section[1]/div/div/a/span',
    "like_count": '//*[@id="global"]/div[2]/div[2]/div/div[4]/section[1]/div/div/div/span/span[2]',
    "author": '//*[@id="global"]/div[2]/div[2]/div/div[4]/section[1]/div/div/div/a/span',
    "url": '//*[@id="global"]/div[2]/div[2]/div/div[4]/section[1]/div/a[1]',
    "hottest": '/html/body/div[4]/div/li[3]',
    "dropdown_container": '//*[@id="global"]/div[2]/div[2]/div/div[1]/div[2]/div',
    "subtitles": '//*[@id="global"]/div[2]/div[2]/div/div[last()-2]/div/div/div[2]',
    # 有品牌有子标题 //*[@id="global"]/div[2]/div[2]/div/div[4]/div/div/div[2]
    # 无品牌有子标题 //*[@id="global"]/div[2]/div[2]/div/div[3]/div/div/div[2]
    "qrcode": '//*[@id="qrcode"]/img',
    "login_btn": '//*[@id="login-btn"]/span',
    "user_profile": '//*[@id="global"]/div[2]/div[1]/ul/li[4]/div/a'
}

mail_config = {
    "smtp_server": "smtp.163.com",
    "smtp_port": 25,
    "smtp_username": "csveni@163.com",
    "smtp_password": "QTGGPSJDUCBROTTM"
}

client = consul.Consul(host='8.138.58.80', port=8500)
client.kv.put('xhs_crawler/elements', json.dumps(elements))
client.kv.put('xhs_crawler/mail_config', json.dumps(mail_config))

xhs_crawler = XHSCrawler("https://www.xiaohongshu.com/explore", "WIS",
                         pool=CookiePool(host="43.139.80.71", port=6378, db=3, password="dsfkjojo432rn5"),
                         headless=False)
EmailUtil.send_email(['1948160779@qq.com'], '爬虫开始', '')
xhs_crawler.do_login()
dict = xhs_crawler.get_page_info()

# import consul
#
# # 创建 Consul 客户端连接
# client = consul.Consul(host='8.138.58.80', port=8500)
#
# # 定义要监听的键
# key = 'schedule/elements'
#
#
# def handle_change(index, data):
#     # 处理键值变化的逻辑，这里简单示例发送 HTTP 请求
#     value = data['Value'].decode('utf-8')
#     print(f"键 '{key}' 的值变化为: {value}")
#
#
# # 注册 Watcher
# index, data = client.kv.get(key)
# if data:
#     current_index = data['ModifyIndex']
# else:
#     current_index = 0
#
# client.watch(key, current_index, handle_change)
#
# # 持续监听
# while True:
#     pass
