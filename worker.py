import threading
import uuid
import comcommander as COM
import Queue

class threadWorker (threading.Thread):
    """
    Class for performing a puppet noop in a thread.
    """

    def __init__(self, listWorkQueue):
        threading.Thread.__init__(self)
        self.ID = uuid.uuid4()		# Uniqueue identifier
        self.listWorkQueue = listWorkQueue

    def run(self):
        while(True):
            for queue in COM.listWorkQueues:
                try:
                    workItem = queue.get_nowait()
                except Queue.Empty:
                    #skip work item
                    continue
                workItem.Run()
                queue.task_done()

