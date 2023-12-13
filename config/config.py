import dataclasses


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
class Config:
    task_rpc_endpoint = ""
    task_dispatcher_redis: RedisConfig = None
    cookie_pool_redis: RedisConfig = None
    mail_config: MailConfig = None
    page_elements: dict = None

    server_port = 0
