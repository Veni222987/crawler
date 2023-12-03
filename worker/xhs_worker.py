from dataclasses import dataclass
from typing import Type

from async_schedule.client import TaskRpcClient
from async_schedule.dispatcher import TaskDispatcher
from async_schedule.op import TaskOperator
from async_schedule.worker import AbstractWorker

from core.xhs_crawler import XHSCrawler


@dataclass
class XHSWorkerContext:
    type: str
    keyword: str


class XHSWorker(AbstractWorker[XHSWorkerContext]):
    def work(self, op: TaskOperator, task_context: XHSWorkerContext):
        xhs_crawler = XHSCrawler("https://www.xiaohongshu.com/explore", task_context.keyword)
        xhs_crawler.do_login()
        data = xhs_crawler.get_page_info()
        xhs_crawler.save_data(data)

    def get_task_context_type(self) -> Type[XHSWorkerContext]:
        return XHSWorkerContext


if __name__ == '__main__':
    # 任务管理server
    client = TaskRpcClient("http://8.138.58.80:8081")

    # 提交任务，一般在前端使用，这里仅作测试（context传入TestWorkerContext结构序列化后的JSON字符串）
    # task_client.submit_task(Task(task_type="test", context=ctx_str))

    # 初始化任务分发器
    dispatcher = TaskDispatcher(client, redis_host="43.139.80.71",
                                redis_port=6378, db=3, redis_pass="dsfkjojo432rn5")

    # 注册任务分发器的任务worker（任务类型 -> 任务worker）
    dispatcher.register_task_worker({"test": XHSWorker(max_running_task_num=5)})
    dispatcher.work()
