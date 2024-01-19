import threading

import consul

import pymysql
from async_schedule.client import TaskRpcClient
from async_schedule.dispatcher import TaskDispatcher
from flask import Flask
from flask_injector import FlaskInjector
from injector import inject
from app.controller.k_task_interface import main_bp
from app.services.k_task_service import KTaskService, KTaskServiceImpl
from config.config_loader import loader
from app.model.k_task import db
from worker.xhs_worker import XHSWorker
from utils.ini2json import mysql_section_to_json_string

app = Flask("xhs_crawler")
app.register_blueprint(main_bp, url_prefix='')
client: TaskRpcClient = None

# 初始化数据库配置
ini_file_path = 'config.ini'
json_string = mysql_section_to_json_string(ini_file_path)

_client = consul.Consul(host='8.138.58.80', port=8500)
_client.kv.put('xhs_crawler/mysql_config', json_string)
mysql_config = loader.load_all().mysql_config


def initialize_app():
    # 初始化数据库
    connection = pymysql.connect(host=mysql_config.host, user=mysql_config.username, password=mysql_config.password)

    # 创建数据库
    with connection.cursor() as cursor:
        cursor.execute('CREATE DATABASE IF NOT EXISTS xhs_crawler')

    # 关闭连接
    connection.close()

    app.config[
        'SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{mysql_config.username}:{mysql_config.password}@{mysql_config.host}:{mysql_config.port}/{mysql_config.database}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 存储client
    app.config['CLIENT'] = client

    # 注册 FlaskInjector
    FlaskInjector(app=app, modules=[lambda binder: configure(binder, db, app)])

    # 初始化数据库
    db.init_app(app)

    # 创建表
    with app.app_context():
        db.create_all()


@inject
def configure(binder, db, app):
    # 绑定 KTaskService 到工厂函数
    binder.bind(interface=KTaskService, to=KTaskServiceImpl(db=db, app=app))


if __name__ == '__main__':
    # 任务管理server
    client = TaskRpcClient("https://async-scheduler.bv5a7f4ddoqnm.ap-southeast-1.cs.amazonlightsail.com")

    # 初始化任务分发器
    dispatcher = TaskDispatcher(client, redis_host="43.139.80.71",
                                redis_port=6378, db=3, redis_pass="dsfkjojo432rn5")

    # 注册任务分发器的任务worker（任务类型 -> 任务worker）
    dispatcher.register_task_worker({"search_xhs": XHSWorker(max_running_task_num=5, headless=False)})
    threading.Thread(target=dispatcher.work).start()

    with app.app_context():
        initialize_app()
    app.json.ensure_ascii = False
    app.run(port=5001, host="0.0.0.0")
