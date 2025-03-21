from pydantic import BaseModel, networks
from uuid import UUID
from enum import Enum

class BlrecUserInfo(BaseModel):
    name: str
    gender: str
    face: networks.AnyHttpUrl
    uid: int
    level: int
    sign: str

class BlrecRoomInfo(BaseModel):
    uid: int
    room_id :int
    short_room_id: int
    area_id: int
    area_name: str
    parent_area_id: int
    parent_area_name: str
    live_status: int
    live_start_time: int
    online: int
    title: str
    cover: networks.AnyHttpUrl
    tags: str
    description: str

class BlrecDiskUsage(BaseModel):
    total: int
    used: int
    free: int

class BlrecSecondaryData(BaseModel):
    'BLREC Webhook data字段的数据格式'
    user_info: BlrecUserInfo | None = None
    room_info: BlrecRoomInfo | None = None
    path: str | None = None
    room_id: int | None = None
    threshold: int | None = None
    usage: BlrecDiskUsage | None = None
    name: str | None = None
    detail: str | None = None
    
class BlrecType(str, Enum):
    'BLREC事件类型'
    LiveBeganEvent = "LiveBeganEvent"
    LiveEndedEvent = "LiveEndedEvent"
    RoomChangeEvent = "RoomChangeEvent"
    RecordingStartedEvent = "RecordingStartedEvent"
    RecordingFinishedEvent = "RecordingFinishedEvent"
    RecordingCancelledEvent = "RecordingCancelledEvent"
    VideoFileCreatedEvent = "VideoFileCreatedEvent"
    VideoFileCompletedEvent = "VideoFileCompletedEvent"
    DanmakuFileCreatedEvent = "DanmakuFileCreatedEvent"
    DanmakuFileCompletedEvent = "DanmakuFileCompletedEvent"
    RawDanmakuFileCreatedEvent = "RawDanmakuFileCreatedEvent"
    RawDanmakuFileCompletedEvent = "RawDanmakuFileCompletedEvent"
    VideoPostprocessingCompletedEvent = "VideoPostprocessingCompletedEvent"
    SpaceNoEnoughEvent = "SpaceNoEnoughEvent"
    Error = "Error"

class BlrecWebhookData(BaseModel):
    'BLREC Webhook的数据格式'
    id: UUID
    date: str
    type: BlrecType
    data: dict

class MessageType(str, Enum):
    '要获取的消息类型'
    all = "all"
    latest = "latest"