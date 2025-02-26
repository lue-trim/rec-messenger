# rec-messenger
把[blrec](https://github.com/lue-trim/blrec)的webhook消息（开始/停止录制、录播异常、录播空间不足等）推送到[修改版HarukaBot](https://github.com/lue-trim/haruka-bot)或者[Qmsg推送机器人](https://qmsg.zendee.cn/)
## 使用方法
### 参照`config.toml`设置一下
- `messenger`处可以设置messenger自身监听的主机和端口号
- `qmsg`处是留给[Qmsg推送机器人](https://qmsg.zendee.cn/)的推送接口设置（目前已经弃用但是接口还留着），如果不想通过HarukaBot推送，改用Qmsg机器人推送的话可以把`enabled`打开并填写推送用的密钥`key`
- `blrec`处就是访问blrec的URL，用来获取主播的昵称的（不然推送消息只显示一个UID稍微有点单调）
### 然后至于怎么运行嘛..
- 参考[autorec](https://github.com/lue-trim/autorec)的运行方法吧（
