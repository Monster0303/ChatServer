# ChatServer

实现聊天室功能

- 支持多客户端连接；
- 支持上下线提醒：
- 每个客户端使用单独的消息队列，防止漏读消息

# Server 端实现了以下 5 中架构

1. [UDP_Socket](https://github.com/Monster0303/ChatServer/blob/main/UDP_Socket.py)：直接使用底层 Socket（UDP）；
2. [TCP_Socket](https://github.com/Monster0303/ChatServer/blob/main/TCP_Socket.py)：直接使用底层 Socket；
3. [TCP_FileMode](https://github.com/Monster0303/ChatServer/blob/main/TCP_FileMode.py)：将底层 Socket 包装成文件形式，可直接以操作文件的形式操作；
4. [TCP_socketserver](https://github.com/Monster0303/ChatServer/blob/main/TCP_socketserver.py)：使用 socketserver 模块；
5. [TCP_Multiple_IO](https://github.com/Monster0303/ChatServer/blob/main/TCP_Multiple_IO.py)：使用 selectors 模块实现 IO 多路复用；

- 关于 socketserver 模块，查看[博客](https://monster0303.gitee.io/posts/19c246fb/#SocketServer)
- 关于 selectors 模块，查看[博客](https://monster0303.gitee.io/posts/19c246fb/#selectors-库)

# 客户端

1. [UDP_Client](https://github.com/Monster0303/ChatServer/blob/main/UDP_Client.py)：基于 UDP 的客户端。
2. MAC 下可使用 [SSokit](https://github.com/rangaofei/SSokit-qmake) 工具调试；
