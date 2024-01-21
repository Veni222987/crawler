import json

import consul

from config.config import Config, MailConfig, MySQLConfig


class ConsulClassLoader:
    def __init__(self, consul_client, project):
        self.consul_client = consul_client
        self.project = project

    def load(self, env):
        # 从consul中获取配置 key
        key = f"{self.project}/{env}"
        _, data = self.consul_client.kv.get(key)
        if data is not None:
            return data["Value"].decode()
        return None

    def load_all(self) -> Config:
        conf = Config()
        # 从consul中获取配置 key
        conf.page_elements = json.loads(self.load("elements"))
        m_conf = json.loads(self.load("mail_config"))
        conf.mail_config = MailConfig(m_conf["smtp_server"], m_conf["smtp_port"], m_conf["smtp_username"],
                                      m_conf["smtp_password"])
        # 从consul中获取MySQL配置， 然后初始化MySQLConfig对象
        mysql_conf = json.loads(self.load("mysql_config"))
        conf.mysql_config = MySQLConfig(mysql_conf["host"], mysql_conf["port"], mysql_conf["username"],
                                        mysql_conf["password"], mysql_conf["database"])

        return conf


loader = ConsulClassLoader(consul.Consul(host='8.138.58.80', port=8500), "xhs_crawler")
