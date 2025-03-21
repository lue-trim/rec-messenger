from fastapi import FastAPI
import json, multiprocessing, functools, toml, requests

from models import BlrecType, BlrecSecondaryData, MessageType
from uuid import UUID

class StaticValues():
    settings = dict()
    message_queue = multiprocessing.Queue()

async def send_msg():
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

async def webhook_handle(json_data, direct_send=True):
    '处理发送的webhook消息'
    # 预处理
    data = json.dumps(json_data['data'])
    date = json_data['date']
    event_type = json_data['type']

    # 根据事件类型分别发送不同信息
    if event_type == BlrecType.Error:
        msg = f"""\
录制异常
时间：
{date}
详情：
{data}
"""
    elif event_type == BlrecType.SpaceNoEnoughEvent:
        msg = f"""警告：录播磁盘空间不足"""

    else: 
        # 需要获取房间号
        room_id = json_data['data']['room_info']['room_id']
        try:
            rec_info = await get_blrec_data(room_id=room_id)
            user_name = rec_info['user_info']['name']
        except Exception:
            user_name = str(room_id)[:3] + "***"
        title = json_data['data']['room_info']['title']
        area_name = json_data['data']['room_info']['area_name']

        if event_type == BlrecType.RecordingStartedEvent:
            msg = f"""\
{user_name} 录制开始
时间：{date}
标题：{title}
分区：{area_name}
"""

        elif event_type == BlrecType.RecordingFinishedEvent:
            msg = f"""\
{user_name} 录制结束
时间：{date}
标题：{title}
分区：{area_name}
"""

    # 发送
    StaticValues.message_queue.put(msg)
    if direct_send:
        await send_msg() 

async def get_blrec_data(room_id):
    '获取房间信息'
    import requests
    blrec_url = StaticValues.settings['blrec']['url']
    url = f"{blrec_url}/api/v1/tasks/{room_id}/data"
    response = requests.get(url=url)
    response_json = response.json()

    return response_json

async def test():
    '测试用例'
    send_msg()

with open("config.toml", 'r', encoding='utf-8') as f:
    StaticValues.settings = toml.load(f)

app = FastAPI()

@app.post("/")
async def get_blrec_message(data: BlrecSecondaryData, date: str, type: BlrecType, id: UUID):
    '处理blrec post过来的消息'
    json_data = {"data": data, "date": date, "type": type, "id": id}
    await webhook_handle(json_data=json_data, direct_send=StaticValues.settings['qmsg']['enabled'])
    return {"code": 200, "message": "mua!"}

@app.get("/")
async def return_blrec_message(msgtype=MessageType.latest):
    '返回消息'
    msg_queue = StaticValues.message_queue
    if not msg_queue.empty():
        if msgtype is MessageType.latest:
            # 只回复最新的
            msg = msg_queue.get()
        elif msgtype is MessageType.all:
            # 我全都要
            qlist = [msg_queue.get() for _ in range(msg_queue.qsize())]
            msg = functools.reduce(lambda x,y:f"{x}; \n{y}", qlist)
            StaticValues.message_queue = multiprocessing.Queue()
        else:
            msg = '未知请求'
    else:
        msg = ''
    return {"code": 200, "message": msg}
