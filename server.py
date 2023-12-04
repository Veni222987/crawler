import csv
import io
import json
import os
import threading

from async_schedule.client import TaskRpcClient
from async_schedule.dispatcher import TaskDispatcher
from async_schedule.domain import Task
from flask import Flask, request, Response

from worker.xhs_worker import XHSWorker, XHSWorkerContext

app = Flask("xhs_crawler")
client: TaskRpcClient = None


@app.route("/search", methods=["POST"])
def search_brand():
    data = request.json
    keyword = data["keyword"]
    ctx_str = json.dumps(XHSWorkerContext(type="search", keyword=keyword).__dict__)
    client.submit_task(Task(task_type="test", context=ctx_str))
    return {"code": 0, "msg": "success", "data": None}


def check_and_return_json(file_path):
    # 检查文件是否存在
    if os.path.exists(file_path):
        # 读取并返回文件内容
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        # 文件不存在，返回空
        return None


@app.route("/result", methods=["GET"])
def get_search_result():
    keyword = request.args.get("keyword")
    # 判断./output/keyword.json是否存在，若存在则返回，否则返回空
    json_result = check_and_return_json("./output/" + keyword + ".json")
    if json_result:
        # 使用 StringIO 作为文件对象
        si = io.StringIO()
        cw = csv.DictWriter(si, fieldnames=json_result[0].keys())
        cw.writeheader()
        cw.writerows(json_result)
        # 设置 Response 对象
        output = Response(si.getvalue(), mimetype='text/csv')
        output.headers["Content-Disposition"] = "attachment; filename=data.csv"
        return output
    return {"code": -1, "msg": "任务未完成"}


if __name__ == '__main__':
    # 任务管理server
    client = TaskRpcClient("http://8.138.58.80:8081")

    # 提交任务，一般在前端使用，这里仅作测试（context传入TestWorkerContext结构序列化后的JSON字符串）
    # task_client.submit_task(Task(task_type="test", context=ctx_str))

    # 初始化任务分发器
    dispatcher = TaskDispatcher(client, redis_host="43.139.80.71",
                                redis_port=6378, db=3, redis_pass="dsfkjojo432rn5")

    # 注册任务分发器的任务worker（任务类型 -> 任务worker）
    dispatcher.register_task_worker({"search": XHSWorker(max_running_task_num=5)})

    t = threading.Thread(target=app.run)
    t.start()
    dispatcher.work()
