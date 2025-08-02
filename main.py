from fastapi import FastAPI
from fastapi import Depends, Request, HTTPException
from ipaddress import ip_address

import json, toml, random, traceback
import asyncio, uvicorn

import songlist
from messenger import return_message, receive_blrec_message

# from loguru import logger
from models import BlrecWebhookData, BlrecType
from static import config, logger

async def test():
    '测试用例'
    send_msg()

# logger.add("debug.log", enqueue=True, level="DEBUG")
app = FastAPI()

### BLREC Webhook
def check_ip (req: Request):
    '检查IP是否在许可范围内'
    # 检查XFF
    default_host = req.client.host
    ip_list = req.headers.get("X-Forwarded-For", f",{default_host}").split(",")
    real_ip = ip_list[-1].strip()
    request_ip = ip_address(real_ip)
    
    # 确定哪些IP可允许
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
    await receive_blrec_message(item)
    return {"code": 200, "message": "mua!"}


### 获取消息
@app.get("/")
async def get_message(type:str="latest", ip_check=Depends(check_ip)):
    '返回消息'
    return await return_message(type)


### 随机歌单
@app.get("/rndsong/list")
async def get_rndsong_list():
    '获取随机叽歌列表'
    songlist = config.app['songlist']
    return {"code": 200, "data": json.dumps(songlist)}

@app.get("/rndsong")
async def get_rnd_wasesong():
    '返回一首随机叽歌'
    return songlist.get_response("web")

@app.get("/rndsong/app")
async def get_rnd_wasesong_app():
    '返回一首随机叽歌并且直接跳转到B站'
    return songlist.get_response("app")

@app.get("/rndsong/webapp")
async def get_rnd_wasesong_webapp():
    '尝试用B站APP自带浏览器打开一首随机叽歌'
    return songlist.get_response("webapp")

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=config.app['host'],
        port=config.app['port']
        )
