import json
import consul
from core.cookie_pool import CookiePool
from core.xhs_crawler import XHSCrawler

# 小红薯=========================================================
xhs_elements = {
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
    "subtitles": '//*[@id="global"]/div[2]/div[2]/div/div[last()-2]',
    # 有品牌有子标题 //*[@id="global"]/div[2]/div[2]/div/div[4]/div/div/div[2]
    # 无品牌有子标题 //*[@id="global"]/div[2]/div[2]/div/div[3]/div/div/div[2]
    # //*[@id="global"]/div[2]/div[2]/div/div[3]/div/div/div[2]/button[1]
    # //*[@id="global"]/div[2]/div[2]/div/div[3]/div/div/div/button[1]

    "qrcode": '//*[@id="qrcode"]/img',
    "login_btn": '//*[@id="login-btn"]/span',
    "user_profile": '//*[@id="global"]/div[2]/div[1]/ul/li[4]/div/a',
    'subtitles_scroller': '//*[@id="global"]/div[2]/div[2]/div/div[last()-2]/div/div/div[1]/div'
    # 有品牌有子标题   //*[@id="global"]/div[2]/div[2]/div/div[4]/div/div/div[1]/div
    # 无品牌有子标题   //*[@id="global"]/div[2]/div[2]/div/div[3]/div/div/div[1]/div
}

# 抖音============================================================
dy_elements = {
    'search_input': '//*[@id="douyin-header"]/div[1]/header/div/div/div[1]/div/div[2]/div/div/input',
    'qrcode': '//*[@id="web-login-container"]/article/article/article/div[2]/div/div[1]/img',
    'mine': '//*[@id="douyin-header"]/div[1]/header/div/div/div[2]/div/div/div[5]/div/a/div',
    'user_id': '//*[@id="douyin-right-container"]/div[2]/div/div/div[2]/div[2]/div[1]/h1/span/span/span/span/span/span',
    'video_btn': '//*[@id="search-content-area"]/div/div[1]/div[1]/div[2]/span[2]',
    'drop_down': '//*[@id="search-content-area"]/div/div[1]/div[1]/div/div/span',
    'hottest': '',
    'subtitles_bar': '//*[@id="search-content-area"]/div/div[1]/div[3]/div/div[1]',
    'subtitles_scroller': '//*[@id="search-content-area"]/div/div[1]/div[3]/div/div[4]/svg[2]/circle',
    'notes_div': '//*[@id="search-content-area"]/div/div[3]/div[2]/ul'

}
# B站============================================================
bilibili_elements = {

}

mail_config = {
    "smtp_server": "smtp.163.com",
    "smtp_port": 25,
    "smtp_username": "csveni@163.com",
    "smtp_password": "QTGGPSJDUCBROTTM"
}

# 更新consul配置
client = consul.Consul(host='8.138.58.80', port=8500)
client.kv.put('xhs_crawler/xhs_elements', json.dumps(xhs_elements))
client.kv.put('xhs_crawler/dy_elements', json.dumps(dy_elements))
client.kv.put('xhs_crawler/bilibili_elements', json.dumps(bilibili_elements))
client.kv.put('xhs_crawler/mail_config', json.dumps(mail_config))
