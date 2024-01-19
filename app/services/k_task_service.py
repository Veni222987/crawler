from flask_sqlalchemy import SQLAlchemy
from injector import inject

from app.model.k_task import KTask
from flask import current_app as app


class KTaskService:
    @inject
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def get_one_by_keyword(self, keyword):
        pass

    def create_task(self, keyword, task_id):
        pass

    def select_platform(self, platform):
        pass

    def get_one_by_task_id(self, task_id):
        pass


class KTaskServiceImpl(KTaskService):
    def __init__(self, db, app):
        super().__init__(db)
        self.db = db
        self.app = app

    def __call__(self) -> KTaskService:
        return KTaskService(db=self.db)

    def create_task(self, keyword, task_id):
        new_k_task = KTask(keyword=keyword, task_id=task_id)
        with app.app_context():
            self.db.session.add(new_k_task)
            self.db.session.commit()

    # @staticmethod
    def get_one_by_keyword(self, keyword):
        k_task = KTask.query.filter_by(keyword=keyword).first()
        return k_task

    # @staticmethod
    def get_one_by_task_id(self, task_id):
        k_task = KTask.query.filter_by(task_id=task_id).first()
        return k_task

    def select_platform(self, platform):
        # 根据platform值返回对应的type
        if platform == "抖音":
            return "search_dy"
        elif platform == "小红书":
            return "search_xhs"
        elif platform == "B站":
            return "search_bilibili"
        else:
            return "search_xhs"
