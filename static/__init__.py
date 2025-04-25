import toml, os

class __Config:
    __app:dict
    __qmsg:dict
    __blrec:dict

    def __init__(self, config_path="config.toml"):
        if os.path.exists(config_path):
            self.load(config_path)
        else:
            self.create_default()

    @property
    def app(self):
        'api设置'
        return self.__app

    @property
    def blrec(self):
        'blrec设置'
        return self.__blrec

    @property
    def qmsg(self):
        'qmsg设置'
        return self.__qmsg

    def create_default(self):
        '创建配置'
        with open("config.toml", 'w', encoding='utf-8') as f:
            default_config = """
[messenger]
host = "localhost"
port = 23561
ip_whitelist = [ # 允许使用post接口和获取消息的源IP
    '127.0.0.1'
]
songlist = [ # av号, 一行一个
    931125260,
    721474979
]

[qmsg]
enabled = false
key = "60d3ffb38dff381c8178cfa75c7e8315"

[blrec]
url = "http://localhost:2356"
            """

            f.write(default_config)

    def load(self, config_path="config.toml"):
        '加载配置'
        with open(config_path, 'r', encoding='utf-8') as f:
            config_file = toml.load(f)
            self.__app = config_file['messenger']
            self.__qmsg = config_file['qmsg']
            self.__blrec = config_file['blrec']

config = __Config()
