import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')


def show_threads(interval: int = 2, event=threading.Event()):
    """
    使用这个函数查看当前进程运行的线程状态
    """

    def _show_threads():
        while not event.wait(interval):
            logging.info(f'thread_number: {threading.active_count()}')
            logging.info([i.getName() for i in threading.enumerate()])
            logging.info('===')

    threading.Thread(target=_show_threads, name='show_threads', daemon=True).start()
