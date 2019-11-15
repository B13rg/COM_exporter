import threading
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from Queue import Queue
import uuid, re
from subprocess import check_output, CalledProcessError
import TaskTypes.example_TT as example_TT

# Create 2 queues, worker queue and display queue
# When a new request is received (from web interface) the work item is added to the queue
listWorkQueues = []

# This is the work item class that describes work that needs to be done by a worker
class WorkItem:
    def __init__(self, taskFunc, RetQueue):
        self.Task = taskFunc			# Worker function to be called
        self.RetQueue = RetQueue  # Queue in which to return this work item once complete
        self.ID = uuid.uuid4()		# Uniqueue identifier
        # Current status of work item (Ready, InProgress, Complete, Failed)
        self.Status = 'Ready'
        # Output of command(s) in prometheus-friendly format
        self.Output = None
        self.ExitCode = 0

    def Run(self):
        self.Status = 'InProgress'
        try:
            self.Output = self.Task()
            self.RetQueue.put(self)
            self.Status = 'Complete'
            return
        except:
            self.Status = 'Failed'
            self.ExitCode = 1

    def IsComplete(self):
        return self.Status == 'Complete'

    def IsFailed(self):
        return self.Status == 'Failed'

class WorkCommander:
    """
    A class that takes a given work type that prepares and starts each script
    """

    def __init__(self, workFuncs):
        self.ID = uuid.uuid4()		# Uniqueue identifier
        self.QWork = Queue()
        self.QDisplay = Queue()
        self.WorkFuncs = workFuncs
        self.OutputString = ""
        pass

    def run(self):
        # Add our work to to the list of work queues
        listWorkQueues.append(self.QWork)
        self.FetchWork()        
        # Wait until our queue has finished
        self.QWork.join()
        listWorkQueues.remove(self.QWork)
        self.ProcessCompletedWork()
        return self.OutputString

    def FetchWork(self):
        """
        Fetches work for a given type, creates a WorkItem for each script, and places them in self.QWork
        """
        for func in self.WorkFuncs:
            self.QWork.put((WorkItem(func,self.QDisplay)))
        return

    def ProcessCompletedWork(self):
        self.OutputString = ""
        while(True):
            try:
                workItem = self.QDisplay.get_nowait()
                self.OutputString = self.OutputString + workItem.Output + "\n"
                self.QDisplay.task_done()
            except:
                pass
