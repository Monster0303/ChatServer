import socketserver
import threading
import logging
from show_threads import show_threads

logging.basicConfig(level=logging.INFO, format='%(message)s')

# 自定义 hanlder，必须是 BaseRequestHandler 的子类。也可以继承 StreamRequestHandler 类，这个类实现了把 socket 包装成文件
class MyHandler(socketserver.BaseRequestHandler):
    clients = {}

    def setup(self) -> None:
        self.event = threading.Event()
        self.clients[self.client_address] = self.request
        logging.info(f'{self.client_address} add in')

    def handle(self) -> None:
        while not self.event.is_set():
            try:
                data: str = self.request.recv(1024).decode()
            except Exception as e:
                logging.warning(f'recv:  {e}')
                data = 'quit'

            if data == 'quit' or data == '':
                break

            msg = f'{self.client_address} msg is: {data}'
            logging.info(msg)

            for c in self.clients.values():
                c.send(msg.encode())

    def finish(self) -> None:
        self.event.set()
        self.clients.pop(self.client_address)
        logging.info(f'{self.client_address} out')


def main():
    try:
        # 实例化一个 socketserver 对象，并指定你自定义的 Handler
        server = socketserver.ThreadingTCPServer(('192.168.199.206', 9999), MyHandler)
        # server.daemon_threads = True    # 默认值是 False，继承自 ThreadingMixIn 类。这意味着只有退出创建的所有线程后，ThreadingMixIn 才会退出。
        threading.Thread(target=server.serve_forever).start()
        while True:
            cmd = input('>>>')
            if cmd == 'stop':
                break
        server.shutdown()
        server.server_close()
    except Exception as e:
        logging.info(e)


if __name__ == '__main__':
    show_threads()
    main()
