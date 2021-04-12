
import time
import threading
import socket
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')


class ChatServer_TCP:
    def __init__(self, ip: str, port: int):
        self.agents = {}
        self.main_socket = socket.socket()
        self.address = (ip, port)
        self.event = threading.Event()

    # 启动监听 socket
    def start(self):
        self.main_socket.bind(self.address)
        self.main_socket.listen()
        threading.Thread(target=self.__conn, name='conn').start()

    # 停止
    def stop(self):
        for s in self.agents:
            s.close()
        self.main_socket.close()
        self.event.set()

    # 等待客户端连接
    def __conn(self):
        while not self.event.is_set():
            agent = self.main_socket.accept()   # 阻塞等待新连接到来
            so, addr = agent
            self.agents[addr] = so
            logging.info(f'{addr} add in')
            threading.Thread(target=self.__revc, args=(so, addr), name='revc').start()

    # 已建立连接
    def __revc(self, so: socket.socket, addr: any):
        while not self.event.is_set():
            try:
                data = so.recv(10240)    # 阻塞等待发消息
            except Exception as e:  # 捕获到异常，按退出处理
                logging.info(e)
                data = b'quit'

            data = data.decode()

            # 退出机制
            if data == 'quit' or not data:
                self.agents.pop(addr)
                so.close()
                logging.info(f'{addr} out')
                break

            # 消息分发
            logging.info(data)
            for i in self.agents.values():
                i.send(data.encode())


if __name__ == '__main__':
    t = ChatServer_TCP('192.168.199.206', 25025)
    t.start()


    def status():
        while True:
            time.sleep(2)
            logging.info(f'thread_number: {threading.active_count()}')
            logging.info(f'agent_number: {len(t.agents)}')
            logging.info([i.getName() for i in threading.enumerate()])
            logging.info('====================================')


    threading.Thread(target=status, name='status', daemon=True).start()

    while True:
        cmd = input('>>>>>>>>>>>>>>>>>>>>')
        if cmd == 'quit':
            t.stop()
            break
