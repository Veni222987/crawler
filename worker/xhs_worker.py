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