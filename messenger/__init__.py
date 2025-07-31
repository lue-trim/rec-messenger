import json, toml, random, traceback, asyncio

from aiohttp import ClientSession, ClientTimeout

# from loguru import logger
from models import BlrecWebhookData, BlrecType
from static import config, logger


class StaticValues():
    message_queue = asyncio.Queue(maxsize=10)

async def _request(timeout=0, **kwargs):
    async with ClientSession(timeout=ClientTimeout(total=timeout)) as session:
        async with session.request(**kwargs) as res:
            response = await res.json()
            if not res.ok:
                logger.error(f"Request error: \n{response}")
                return {}
            else:
                return response

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
    response = await _request(method="post", url=url, data=data, headers=headers)
    #response = requests.post(url=url, data=json.dumps(data), headers=headers)
    data = response.json()

    # 获取结果
    print(data)

async def webhook_handle(json_data, direct_send=True):
    '处理发送的webhook消息'
    # 预处理
    # data = json.dumps(json_data['data'])
    data = json_data['data']
    date = json_data['date']
    event_type = json_data['type']

    # 根据事件类型分别发送不同信息
    if event_type == BlrecType.Error:
        msg = f"""\
**录制异常**
```
{data}
```
---
> 时间: {date}
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
            user_name = str(room_id)
            logger.warning(f"抓取直播信息失败: \n{traceback.format_exc()}")
        title = json_data['data']['room_info']['title']
        area_name = json_data['data']['room_info']['area_name']

        if event_type == BlrecType.RecordingStartedEvent:
            msg = f"""\
**{user_name} 录制开始**
---
> 时间：{date}
> 标题：{title}
> 分区：{area_name}
"""

        elif event_type == BlrecType.RecordingFinishedEvent:
            msg = f"""\
**{user_name} 录制结束**
---
> 时间：{date}
> 标题：{title}
> 分区：{area_name}
"""

    # 发送
    StaticValues.message_queue.put_nowait(msg)
    if direct_send:
        await send_msg() 

async def get_blrec_data(room_id):
    '获取房间信息'
    blrec_url = config.blrec['url']
    url = f"{blrec_url}/api/v1/tasks/{room_id}/data"
    response_json = await _request(method="get", url=url)
    # response_json = response.json()

    return response_json

async def return_blrec_message(type:str):
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
