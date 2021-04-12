import logging
import socket
import threading
import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')


class ChatServer_UDP:
    def __init__(self, ip, port, interval=60):
        self.address = (ip, port)
        self.main_socket = socket.socket(type=socket.SOCK_DGRAM)
        self.agents = {}
        self.event = threading.Event()
        self.interval = interval

    def start(self):
        self.main_socket.bind(self.address)
        threading.Thread(target=self.__recv).start()
        threading.Thread(target=self.__status, daemon=True).start()

    def stop(self):
        self.main_socket.close()
        self.event.set()

    def __status(self):
        while not self.event.wait(2):
            logging.info(self.agents)

    def __recv(self):
        while not self.event.is_set():
            try:
                data, raddr = self.main_socket.recvfrom(1024)  # 阻塞等消息
            except Exception as e:
                logging.warning(e)
                break

            data = data.strip()
            current = datetime.datetime.now().timestamp()  # 记录当前时间

            if data == b'^hb^':  # 心跳包
                logging.info(data)
                self.agents[raddr] = current
                continue
            elif data == b'^q^':  # 退出指令
                self.agents.pop(raddr)
                logging.info(f'{raddr} out')
                continue
            elif data == b'^a^':  # 加入报告
                self.agents[raddr] = current
                logging.info(f'{raddr} add in')
                continue

            self.agents[raddr] = current  # 普通消息
            data = f'{raddr}: {data.decode()}'
            logging.info(data)

            d = set()  # 超时的客户端集合

            for c, t in self.agents.items():
                if current - t < self.interval:  # 每次要发消息时，判断客户端是否过期
                    self.main_socket.sendto(data.encode(), c)
                else:
                    d.add(c)

            # 清理过期客户端
            for i in d:
                self.agents.pop(i)
                logging.info(f'{i} timeout')


if __name__ == '__main__':
    u = ChatServer_UDP('192.168.199.206', 25025, 60)
    u.start()

    while not u.event.is_set():
        cmd = input('>>>>>')
        if cmd == 'quit':
            u.stop()
            break
