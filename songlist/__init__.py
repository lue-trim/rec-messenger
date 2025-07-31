import random

from static import config, logger
from fastapi.responses import RedirectResponse

def get_return_url(songlist=[], url_type=""):
    '获取返回的URL'
    aid = random.choice(songlist)
    if url_type == "app":
        url = f"bilibili://video/av{aid}"
    elif url_type == "web":
        url = f"https://www.bilibili.com/video/av{aid}"
    else:
        url = f"bilibili://browser/?url=https%3A%2F%2Fapi.luetrim.top%2Frndsong"
    return url

def get_response(url_type=""):
    '获取响应值'
    songlist = config.app['songlist']
    if songlist:
        return RedirectResponse(url=get_return_url(songlist, url_type))
    else:
        return {"code": 500, "message": "Please set up the songs!"}

