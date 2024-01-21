import csv
import io
import json
import os

from injector import inject
from async_schedule.domain import Task, TaskStatus
from flask import Blueprint, request, Response, current_app

from core.xhs_crawler import XHSCrawler
from worker.xhs_worker import XHSWorkerContext
from app.services.k_task_service import KTaskService

main_bp = Blueprint('main', __name__)


def check_and_return_json(file_path):
    # 检查文件是否存在
    if os.path.exists(file_path):
        # 读取并返回文件内容
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        # 文件不存在，返回空
        return None


@inject
@main_bp.route("/search", methods=["POST"])
def search_brand(k_task_service: KTaskService):
    data = request.json
    keyword = data["keyword"]
    filter = data.get("filter", None)
    platform = data.get("platform", "小红书")
    _type = k_task_service.select_platform(platform)
    client = current_app.config['CLIENT']

    try:
        # 根据数据库中是否已经有keyword，若有则获取该记录
        k_task = k_task_service.get_one_by_keyword(keyword)
        if k_task is not None:
            task_id = k_task.task_id
            task = client.get_task(task_id)
            count = XHSCrawler.parse_progress(text=task.stage)
            return {"code": 1, "msg": "任务已经部署", "task_id": task_id, "count": count}

        ctx_str = json.dumps(XHSWorkerContext(type=_type,
                                              keyword=keyword).__dict__)
        task = Task(task_type="search_xhs", context=ctx_str)
        print(task.task_id)
        client.submit_task(task)
        k_task_service.create_task(keyword=keyword, task_id=task.task_id)
    except Exception as e:
        return {"code": -1, "msg": f"任务部署失败, 原因: {str(e)}", "task_id": "", "count": 0}
    return {"code": 0, "msg": "任务部署成功", "task_id": task.task_id, "count": 0}


@inject
@main_bp.route("/result", methods=["GET"])
def get_search_result(k_task_service: KTaskService):
    keyword = request.args.get("keyword")
    # 根据数据库中是否已经有keyword，若有则记录
    k_task = k_task_service.get_one_by_keyword(keyword)
    client = current_app.config['CLIENT']
    if k_task is not None:
        task_id = k_task.task_id
        task = client.get_task(task_id)
        if task.status < TaskStatus.FINAL:
            count = XHSCrawler.parse_progress(text=task.stage)
            return {"code": 1, "task_id": task_id, "count": count, "msg": "任务未完成"}
        output = get_csv_by_keyword(keyword)
        return output
    return {"code": -1, "msg": "任务不存在", "task_id": "", "count": 0}


@inject
@main_bp.route("/progress", methods=["GET"])
def get_search_progress(k_task_service: KTaskService):
    client = current_app.config['CLIENT']
    task_id = request.args.get("task_id")
    k_task = k_task_service.get_one_by_task_id(task_id)
    if k_task is not None:
        keyword = k_task.keyword
        task = client.get_task(task_id)
        count = XHSCrawler.parse_progress(text=task.stage)
        if task.status < TaskStatus.FINAL:
            return {"code": 1, "count": count, "task_id": task_id, "msg": "任务未完成"}
        output = get_csv_by_keyword(keyword)
        return output
    return {"code": -1, "msg": "任务不存在", "task_id": "", "count": 0}


def get_csv_by_keyword(keyword):
    json_result = check_and_return_json("./output/" + keyword + ".json")
    json_result = list(json_result.values())
    # 使用 StringIO 作为文件对象
    si = io.StringIO()
    cw = csv.DictWriter(si, fieldnames=json_result[0].keys())
    cw.writeheader()
    cw.writerows(json_result)
    # 设置 Response 对象
    output = Response(si.getvalue(), mimetype='text/csv')
    output.headers["Content-Disposition"] = "attachment; filename=data.csv"
    return output
