from unittest import TestCase

import consul
from async_schedule.op import TaskOperator
from flask import Flask

from app.controller.k_task_interface import check_and_return_json
from config.config_loader import loader
from app.model.k_task import db, KTask
from core.cookie_pool import CookiePool
from core.xhs_crawler import XHSCrawler
# from server import check_and_return_json

from utils.snowflake import next_id

from utils.ini2json import mysql_section_to_json_string

import pymysql

class Test(TestCase):
    def test_check_and_return_json(self):
        data = check_and_return_json("output/广州.json")
        print(data)

    def test_snowflake(self):
        for _ in range(5):
            generated_id = next_id()
            print("Generated Snowflake ID:", generated_id)

    def test_ini2json(self):
        ini_file_path = '../config.ini'
        json_string = mysql_section_to_json_string(ini_file_path)

        print(json_string)

        client = consul.Consul(host='8.138.58.80', port=8500)
        client.kv.put('xhs_crawler/mysql_config', json_string)

        mysql_config = loader.load_all().mysql_config
        print(mysql_config.host)

    def test_sql(self):
        ini_file_path = '../config.ini'
        json_string = mysql_section_to_json_string(ini_file_path)

        client = consul.Consul(host='8.138.58.80', port=8500)
        client.kv.put('xhs_crawler/mysql_config', json_string)
        mysql_config = loader.load_all().mysql_config

        # 初始化数据库
        connection = pymysql.connect(host=mysql_config.host, user=mysql_config.username, password=mysql_config.password)

        # 创建数据库
        with connection.cursor() as cursor:
            cursor.execute('CREATE DATABASE IF NOT EXISTS xhs_crawler')

        # 关闭连接
        connection.close()

        app = Flask(__name__)

        app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{mysql_config.username}:{mysql_config.password}@{mysql_config.host}:{mysql_config.port}/{mysql_config.database}"
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # 初始化数据库
        db.init_app(app)

        # 创建表
        # db.drop_all()
        with app.app_context():
            db.create_all()

        new_k_task = KTask(keyword='hhh', task_id='123456')

        with app.app_context():
            db.session.add(new_k_task)
            db.session.commit()

            task = KTask.query.filter_by(keyword='hhh').first()
            print(task.id)


    def testCrawler(self):
        xhs_crawler = XHSCrawler("https://www.xiaohongshu.com/explore", "IRY",
                                 pool=CookiePool(host="43.139.80.71", port=6378, db=3, password="dsfkjojo432rn5"),
                                 headless=False)
        xhs_crawler.do_login()
        taskOperator = TaskOperator
        dict = xhs_crawler.get_page_info(taskOperator)
        xhs_crawler.save_data(dict, "IRY")
