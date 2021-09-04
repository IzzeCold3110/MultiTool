import threading
import time


class MainQueue(threading.Thread):
    running = True
    queue = []

    def __init__(self):
        super(MainQueue, self).__init__()

    def check_queue(self):
        if len(self.queue) > 0:
            print(str(len(self.queue))+" items in queue")
            for item in self.queue:
                print("data")
                print(item)
                print("--- item end ---")
                self.queue.remove(item)
                print("removed item: "+item["q_itemName"])

    def run(self) -> None:
        while self.running is True:
            self.check_queue()
            time.sleep(0.1)


class QueueControl:
    def append(self, q_MainQueueThread, data):
        print(q_MainQueueThread.queue)
        q_MainQueueThread.queue.append(data)


def run_queue():
    q_MainQueueThread = MainQueue()
    q_MainQueueThread.start()
    return q_MainQueueThread
