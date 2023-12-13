from config.config import Config


class ConsulClassLoader:
    def __init__(self, consul_client, project):
        self.consul_client = consul_client
        self.project = project

    def load(self, env) -> Config:
        key = f"{self.project}/{env}"
        # TODO 从consul中获取配置 key
        return None


loader = ConsulClassLoader("", "xhs_crawler")  # TODO 传入consul_client
