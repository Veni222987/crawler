import dataclasses
import configparser

_config = configparser.ConfigParser()
_config.read('config.ini')


@dataclasses.dataclass
class RedisConfig:
    host = ""
    port = 0
    db = 0
    password = ""


@dataclasses.dataclass
class MailConfig:
    smtp_server = ""
    smtp_port = 0
    smtp_username = ""
    smtp_password = ""

    def __init__(self, smtp_server, smtp_port, smtp_username, smtp_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password


@dataclasses.dataclass
class MySQLConfig:
    host = ""
    port = 80
    username = ""
    password = ""
    database = ""

    def __init__(self, host, port, username, password, database):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database


@dataclasses.dataclass
class Config:
    task_rpc_endpoint = ""
    task_dispatcher_redis: RedisConfig = None
    cookie_pool_redis: RedisConfig = None
    mail_config: MailConfig = None
    page_elements: dict = None
    mysql_config: MySQLConfig = None
    server_port = 0
