import dataclasses


@dataclasses.dataclass
class RedisConfig:
    host = ""
    port = 0
    db = 0
    password = ""


@dataclasses.dataclass
class Config:
    task_rpc_endpoint = ""
    task_dispatcher_redis: RedisConfig = None
    cookie_pool_redis: RedisConfig = None

    page_elements: dict = None

    server_port = 0
