from fastapi import FastAPI
from fastapi import Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from ipaddress import ip_address
import json, toml, random
import asyncio, requests, uvicorn

# from loguru import logger
from models import BlrecWebhookData, BlrecType
from static import config

class StaticValues():
    message_queue = asyncio.Queue(maxsize=10)

async def send_msg():
    '给bot发消息'
    msg = await StaticValues.message_queue.get()
    KEY = config.qmsg['key']

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
    StaticValues.message_queue.put_nowait(msg)
    if direct_send:
        await send_msg() 

async def get_blrec_data(room_id):
    '获取房间信息'
    import requests
    blrec_url = config.blrec['url']
    url = f"{blrec_url}/api/v1/tasks/{room_id}/data"
    response = requests.get(url=url)
    response_json = response.json()

    return response_json

async def test():
    '测试用例'
    send_msg()

# logger.add("debug.log", enqueue=True, level="DEBUG")
app = FastAPI()

### BLREC Webhook
def check_ip (req: Request):
    '检查IP是否在许可范围内'
    request_ip = ip_address(req.client.host)
    allow_ip_list = [ip_address(ip) for ip in config.app['ip_whitelist']]
    if request_ip not in allow_ip_list:
        raise HTTPException(
            status_code=403, 
            detail="You are unauthorized here."
            )
    else:
        return True
@app.post("/")
async def get_blrec_message(item: BlrecWebhookData|str, ip_check=Depends(check_ip)):
    '处理blrec post过来的消息'
    data = item
    if type(item) is str:
        json_data = json.loads(item)
    else:
        json_data = {"data": data.data, "date": data.date, "type": data.type, "id": data.id}
    await webhook_handle(json_data=json_data, direct_send=config.qmsg['enabled'])
    return {"code": 200, "message": "mua!"}

### 随机歌单
@app.get("/rndsong")
async def get_rnd_wasesong():
    '返回一首随机叽歌'
    songlist = config.app['songlist']
    if songlist:
        aid = random.choice(songlist)
        url = f"https://www.bilibili.com/video/av{aid}"
        return RedirectResponse(url=url)
    else:
        return {"code": 500, "message": "Please set up the songs!"}

### 获取消息
@app.get("/")
async def return_blrec_message(type:str="latest", ip_check=Depends(check_ip)):
    '返回消息'
    msgtype = type
    msg_queue = StaticValues.message_queue
    if not msg_queue.empty():
        if msgtype == "latest":
            logger.debug("latest")
            # 只回复最新的
            msg = await msg_queue.get()
        elif msgtype == "all":
            # 我全都要
            qlist = []
            is_empty = False
            # logger.debug(msg_queue.qsize())
            while not is_empty:
                try:
                    qlist.append(msg_queue.get_nowait())
                except asyncio.QueueEmpty:
                    is_empty = True
            # msg = functools.reduce(lambda x,y:f"{x}; \n{y}", qlist)
            msg = ";\n".join(qlist)
        else:
            msg = '未知请求'
    else:
        msg = ''
    return {"code": 200, "message": msg}

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=config.app['host'],
        port=config.app['port']
        )
