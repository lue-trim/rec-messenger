### ---
### 这个是用来一键获取主页所有视频的，需要自己手动编辑一下
### ---
import asyncio, json, sys

from bilibili_api.user import User

UID = 1950658 # B站UID
TID = 0 # 分区ID，0=全部，1=动画区，3=音乐区，4=游戏区，160=生活区，211=美食区
MAX_PAGES = 1 # 前n页
PS = 20 # 一页n个视频

async def main():
    u = User(uid=UID)
    for i in range(MAX_PAGES):
        videos = await u.get_videos(tid=TID, pn=i+1, ps=PS)
        # json.dump(videos, sys.stdout)

        # 提取标题和aid
        for video in videos['list']['vlist']:
            title = video['title']
            aid = video['aid']
            print(f"{aid}, # {title}")

        # 睡一下，防止请求过于频繁
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
