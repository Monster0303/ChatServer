import logging
import socket
import threading

logging.basicConfig(level=logging.INFO, format='%(message)s')


class ChatClient_UDP:
    def __init__(self, ip, port, interval=10):
        self.address = (ip, port)
        self.main_socket = socket.socket(type=socket.SOCK_DGRAM)
        self.event = threading.Event()
        self.interval = interval

    def start(self):
        threading.Thread(target=self.__recv).start()
        threading.Thread(target=self.__sendhb, daemon=True).start()

    def stop(self):
        self.send('^q^')
        self.main_socket.close()
        self.event.set()

    # 接收消息
    def __recv(self):
        # 发送报道消息
        self.send('^a^')

        while not self.event.is_set():
            try:
                data, clientid= self.main_socket.recvfrom(1024)  # 阻塞接收消息
            except Exception as e:
                logging.warning(e)
                break

            data = data.decode().strip()
            logging.info(f'{clientid}: {data}')

    def send(self, data: str):
        data = data.encode()
        self.main_socket.sendto(data, self.address)

    def __sendhb(self):
        while not self.event.wait(self.interval):
            self.send('^hb^')


u1 = ChatClient_UDP('192.168.50.30', 25025)
u1.start()

while True:
    cmd = input('>>>>>')
    if cmd == 'quit':
        u1.stop()
        break
    else:
        u1.send(cmd)
