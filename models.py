from pydantic import BaseModel
from enum import Enum

class BlrecWebhook(BaseModel):
    'BLREC Webhook的数据格式'
    id: str
    date: str
    type: str
    data: dict

class MessageType(str, Enum):
    '要获取的消息类型'
    all = "all"
    latest = "latest"