from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote, quote, urlparse, parse_qs
import json, multiprocessing, functools, toml, requests

class StaticValues():
    settings = dict()
    message_queue = multiprocessing.Queue()

class RequestHandler(BaseHTTPRequestHandler):
    def reply(self, message="Mua!", code=200):
        '发送服务器响应'
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        data = {
            "code": code,
            "message": message
        }
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        '接收POST消息'
        # 读取参数
        data = self.rfile.read(int(self.headers['content-length']))
        data = unquote(str(data, encoding='utf-8'))
        json_obj = json.loads(data)

        webhook_handle(json_data=json_obj, direct_send=StaticValues['qmsg']['enabled'])
        # 回复
        self.reply()

    def do_GET(self):
        '供外部请求'
        # 读取参数
        params = parse_qs(urlparse(self.path).query)
        # TODO: 支持其他参数
        if params:
            req_type = params.get('type', [''])[0]
            msg_queue = StaticValues.message_queue
            msg = ''
            if req_type == "latest":
                # 只回复最新的
                if not msg_queue.empty():
                    msg = msg_queue.get()
            elif req_type == "all":
                # 我全都要
                qlist = [msg_queue.get() for _ in range(msg_queue.qsize())]
                msg = functools.reduce(lambda x,y:f"{x}; \n{y}", qlist)
                StaticValues.message_queue = multiprocessing.Queue()
            else:
                msg = '未知请求'
        self.reply(message=msg)

def send_msg():
    '给bot发消息'
    msg = StaticValues.message_queue.get()
    KEY = StaticValues.settings['qmsg']['key']

    url = f"https://qmsg.zendee.cn/send/{KEY}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded", 
        #"msg": msg
    }
    data = {
        "msg": msg,
    }

    # 请求API
    response = requests.post(url=url, data=data, headers=headers)
    #response = requests.post(url=url, data=json.dumps(data), headers=headers)
    data = response.json()

    # 获取结果
    print(data)

def webhook_handle(json_data, direct_send=True):
    '处理发送的webhook消息'
    # 预处理
    data = json.dumps(json_data['data'])
    date = json_data['date']
    event_type = json_data['type']

    # 根据事件类型分别发送不同信息
    if event_type == "Error":
        msg = f"""\
录制异常
时间：
{date}
详情：
{data}
"""
    elif event_type == "SpaceNoEnoughEvent":
        msg = f"""警告：录播磁盘空间不足"""

    else: 
        # 需要获取房间号
        room_id = json_data['data']['room_info']['room_id']
        try:
            rec_info = get_blrec_data(room_id=room_id)
            user_name = rec_info['user_info']['name']
        except Exception:
            user_name = str(room_id)[:3] + "***"
        title = json_data['data']['room_info']['title']
        area_name = json_data['data']['room_info']['area_name']

        if event_type == "RecordingStartedEvent":
            msg = f"""\
{user_name} 录制开始
时间：{date}
标题：{title}
分区：{area_name}
"""

        elif event_type == "RecordingFinishedEvent":
            msg = f"""\
{user_name} 录制结束
时间：{date}
标题：{title}
分区：{area_name}
"""

    # 发送
    StaticValues.message_queue.put(msg)
    if direct_send:
        send_msg() 

def get_blrec_data(room_id):
    '获取房间信息'
    import requests
    blrec_url = StaticValues.settings['blrec']['url']
    url = f"{blrec_url}/api/v1/tasks/{room_id}/data"
    response = requests.get(url=url)
    response_json = response.json()

    return response_json

def test():
    '测试用例'
    send_msg()

with open("config.toml", 'r', encoding='utf-8') as f:
    StaticValues.settings = toml.load(f)

if __name__ == "__main__":
    host_server = StaticValues.settings['messenger']['host']
    port_server = StaticValues.settings['messenger']['port']
    # 监听
    addr = (host_server, port_server)
    server = HTTPServer(addr, RequestHandler)
    server.serve_forever()
