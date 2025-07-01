# rec-messenger
- 把[blrec](https://github.com/lue-trim/blrec)的webhook消息（开始/停止录制、录播异常、录播空间不足等）推送到[修改版HarukaBot](https://github.com/lue-trim/haruka-bot)或者[Qmsg推送机器人](https://qmsg.zendee.cn/)  
- v0.2: 新增了一个跳转到B站随机指定视频的功能
## 安装方法
- 可以直接使用[blrec](https://github.com/lue-trim/blrec)的环境
- 然后`git clone`到任意位置并运行`main.py`即可使用（参考[autorec](https://github.com/lue-trim/autorec)的运行方法）

## 使用方法
### 参照`config.toml`设置一下
- `messenger`处可以设置messenger自身监听的主机和端口号，以及配置IP白名单（用于接收和发送blrec的信息）
- `messenger/songlist`处是作为随机歌单后端使用的，往里面放上B站视频av号，浏览器访问`/rndsong`就可以跳转到随机视频页面啦
- `qmsg`处是留给[Qmsg推送机器人](https://qmsg.zendee.cn/)的推送接口设置（目前已经弃用但是接口还留着），如果不想通过HarukaBot推送，改用Qmsg机器人推送的话可以把`enabled`打开并填写推送用的密钥`key`
- `blrec`处就是访问blrec的URL，用来获取主播的昵称的（不然推送消息只显示一个UID稍微有点单调）
### get_songlist.py
这个是用来一键获取对应主播主页的视频的，对于快速填充随机歌单非常好用
