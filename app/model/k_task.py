from flask_sqlalchemy import SQLAlchemy
from utils.snowflake import next_id

db = SQLAlchemy()


class KTask(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    keyword = db.Column(db.String(255), nullable=False)
    task_id = db.Column(db.String(255), nullable=False)

    def __init__(self, keyword, task_id):
        self.id = str(next_id())
        self.keyword = keyword
        self.task_id = task_id
