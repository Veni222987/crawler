import configparser
import json


def mysql_section_to_json_string(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)

    # 检查是否存在 [mysql] 部分
    if 'MySQL' in config:
        # 将 [mysql] 部分的配置转为字典
        mysql_dict = dict(config['MySQL'])

        # 使用 json.dumps() 将字典转为 JSON 格式的字符串
        json_string = json.dumps(mysql_dict, indent=2)  # 可选的 indent 参数用于缩进，方便阅读

        return json_string
    else:
        return None
