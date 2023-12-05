from dataclasses import dataclass
from typing import Type

from async_schedule.op import TaskOperator
from async_schedule.worker import AbstractWorker

from core.xhs_crawler import XHSCrawler


@dataclass
class XHSWorkerContext:
    type: str
    keyword: str


class XHSWorker(AbstractWorker[XHSWorkerContext]):
    def __init__(self, max_running_task_num, headless: bool = True):
        super().__init__(max_running_task_num)
        self.headless = headless

    def work(self, op: TaskOperator, task_context: XHSWorkerContext):
        xhs_crawler = XHSCrawler("https://www.xiaohongshu.com/explore", task_context.keyword, self.headless)
        xhs_crawler.do_login()
        data = xhs_crawler.get_page_info()
        xhs_crawler.save_data(data, task_context.keyword)

    def get_task_context_type(self) -> Type[XHSWorkerContext]:
        return XHSWorkerContext

    def retryable(exception_instance):
        return False
