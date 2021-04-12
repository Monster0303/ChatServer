import time
import threading
import socket
import logging
import selectors
import queue
from show_threads import show_threads

logging.basicConfig(level=logging.INFO, format='%(message)s')


class Conn:
    def __init__(self, conn: socket.socket, handler):
        self.conn = conn
        self.handler = handler
        self.queue = queue.Queue()


class ChatServer_TCP:
    def __init__(self, ip: str, port: int):
        self.main_socket = socket.socket()
        self.address = (ip, port)
        self.event = threading.Event()
        self.selector = selectors.DefaultSelector()
        self.clients = {}

    # 启动监听 socket
    def start(self):
        self.main_socket.bind(self.address)
        self.main_socket.listen()
        self.main_socket.setblocking(False)
        self.selector.register(self.main_socket, selectors.EVENT_READ, self._accept)  # 注册

        # select 会有阻塞，单独启一个线程
        threading.Thread(target=self._select, name='select').start()

    # 停止
    def stop(self):
        self.event.set()
        logging.info('event close')

        c_fb = []
        for i in self.selector.get_map().values():
            c_fb.append(i.fileobj)  # 获取到所有正在监听着的 socket

        for fobj in c_fb:
            self.selector.unregister(fobj)
            fobj.close()
            logging.info('sock close ok')

        try:
            self.selector.close()
            logging.info('selector close ok')
        except OSError:
            pass

    def _select(self):
        while not self.event.is_set():
            try:
                event = self.selector.select()
                """
                这个程序最大的问题，在select()一直判断可写，几乎一直循环不停。所以对于写不频繁的情况下，就不要监听 EVENT_WRITE。
                对于Server来说，一般来说，更多的是等待对方发来数据后响应时才发出数据，而不是积极的等着发送数据。
                所以只监听EVENT_READ，收到数据之后再发送就可以了。
                """
            except OSError:
                return

            # event 的格式:
            # [(SelectorKey(fileobj=<socket.socket fd=3, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('192.168.50.30', 9999)>, fd=3, events=1, data=<bound method ChatServer_TCP.accept of <__main__.ChatServer_TCP object at 0x7ff5797c5f70>>), 1)]

            for key, mask in event:
                # 根据 data，判断触发的是 main_socket 还是 某个客户端的 socket
                if callable(key.data):  # 如果可调用，说明是 main_socket，因为 main_socket 绑定的是 _accept 函数，而函数会返回 True
                    callback = key.data  # key.data = self._accept
                else:  # 如果不可调用，说明是客户端的 socket，因为注册监听时绑定的 data 是个 Conn 实例化的对象，而 Conn 本身没有实现 __call__，所以该对象不可调用，会返回 False
                    callback = key.data.handler  # key.data = class_Conn_object.handler

                callback(key.fileobj, mask)

    # 来新客户端连接时的处理方法
    def _accept(self, socket: socket.socket, mask=None):
        socket, client = socket.accept()  # 不阻塞了
        socket.setblocking(False)

        # 使用 Conn 类将 socket 和 对应的 _handler 函数包装起来，然后添加到客户端的字典中
        self.clients[client] = Conn(socket, self._handler)  # self._handler 只是一个引用，不会复制出多个 _handler

        logging.info(f'{client} add in')

        # 开始监视这个 socket 的读写，data 为 Conn 对象，如果触发，_select 那里会返回一个 Conn 对象
        self.selector.register(socket, selectors.EVENT_READ | selectors.EVENT_WRITE, data=self.clients[client])

    # 已监听客户端的读写操作方法
    def _handler(self, conn: socket.socket, mask):
        remote = conn.getpeername()
        client_conn = self.clients[remote]

        # 读操作 mask 也可能是 3，通过位与判断
        if mask & selectors.EVENT_READ == selectors.EVENT_READ:
            try:
                data: str = conn.recv(10240).decode().strip()  # 不阻塞了
            except Exception as e:  # 捕获到异常，按退出处理
                logging.info(e)
                data = 'quit'

            # 退出机制
            if data == 'quit' or not data:
                self.selector.unregister(conn)
                conn.close()
                self.clients.pop(remote)
                logging.info(f'{remote} out')
                return

            for c in self.clients.values():
                c.queue.put(data)

        # 写操作 mask 也可能是 3，通过位与判断
        if mask & selectors.EVENT_WRITE == selectors.EVENT_WRITE:
            # 因为写一直就绪，mask为2，所以一直可以写，从而导致select()不断循环，如同不阻塞一样
            while not client_conn.queue.empty():
                msg: str = client_conn.queue.get()
                conn.send(msg.encode())


if __name__ == '__main__':
    t = ChatServer_TCP('192.168.199.206', 25025)
    t.start()

    while True:
        cmd = input('>>>>>>>>>>>>>>>>>>>>')
        if cmd == 'stop':
            t.stop()
            break
