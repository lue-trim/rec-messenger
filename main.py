from http.server import HTTPServer, BaseHTTPRequestHandler

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        '接收POST消息'
        from urllib.parse import unquote, quote
        import json
        # 读取参数
        data = self.rfile.read(int(self.headers['content-length']))
        data = unquote(str(data, encoding='utf-8'))
        json_obj = json.loads(data)

        webhook_handle(json_data=json_obj)
        # 回复
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        data = {
            "code": 200,
            "message": "Mua!"
        }
        self.wfile.write(str(data).encode())

def send_msg(msg:str):
    '给bot发消息'
    import json, requests

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

def webhook_handle(json_data):
    '处理发送的webhook消息'
    import json
    
    # 预处理
    data = json.dumps(json_data['data'])
    date = json_data['date']
    event_type = json_data['type']

    # 根据事件类型分别发送不同信息
    if event_type == "Error":
        msg = f"""\
录播异常
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
{user_name} 已开始录制
时间：{date}
标题：{title}
分区：{area_name}
"""

        elif event_type == "RecordingFinishedEvent":
            msg = f"""\
{user_name} 已下播
时间：{date}
标题：{title}
分区：{area_name}
"""

    # 发送
    send_msg(msg) 

def get_blrec_data(room_id):
    '获取房间信息'
    import requests
    url = "http://{}:{}{}".format(host_blrec, port_blrec, '/api/v1/tasks/{}/data'.format(room_id))
    response = requests.get(url=url)
    response_json = response.json()

    return response_json

def test():
    '测试用例'
    from urllib.parse import unquote, quote
    send_msg()

KEY = '60d3ffb38dff381c8178cfa75c7e8315'
host_server = "localhost"
port_server = 23561

host_blrec = "localhost"
port_blrec = 2356

if __name__ == "__main__":
    # 监听
    addr = (host_server, port_server)
    server = HTTPServer(addr, RequestHandler)
    server.serve_forever()
