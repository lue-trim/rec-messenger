### ---
### 根据url_list.json的内容转换成av号, 标题的格式
### ---
import asyncio, json, sys, re

from bilibili_api import video

async def main():
    # 载入
    with open("url_list.json", encoding='utf-8') as f:
        url_list = json.load(f)
    
    p = re.compile(r"(?=BV).*(?=\/)")
    for url in url_list:
        # 匹配
        bvid = re.findall(p, url)[0]
        v = video.Video(bvid=bvid)
        
        # 获取数据
        info = await v.get_info()
        title = info['title']
        bvid = v.get_bvid()
        print(f"'{bvid}', # {title}")

        # 睡一下，防止请求过于频繁
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
