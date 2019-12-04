import Queue
import threading
import time
import uuid

import comcommander as COM


class threadWorker (threading.Thread):
    """Class that monitors a queue for work, then performs the work

    It will monitor the passed in queue indefinitely and perform any work placed into it.
    If there is no work, then it will sleep for 1 seconds before checking again.
    """

    def __init__(self, listWorkQueue):
        threading.Thread.__init__(self)
        self.ID = uuid.uuid4()		# Unique identifier
        self.listWorkQueue = listWorkQueue

    def run(self):
        while(True):
            for queue in COM.ListWorkQueues:
                try:
                    workItem = queue.get_nowait()
                except Queue.Empty:
                    # Skip work item/empty queue
                    # Wait a little bit to not hammer the queue looking for work
                    # Prometheus times out waiting after 10 seconds, so we should be fine unless a job takes >9 seconds...
                    time.sleep(1)
                    continue
                workItem.Run()
                queue.task_done()
