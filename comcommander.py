import logging
import re
import threading
import uuid
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from Queue import Queue
from SocketServer import ThreadingMixIn
from subprocess import CalledProcessError, check_output

# When a new request is received (from web interface) the work item is added to the queue
# This is the list of all workqueues from all request threads.
ListWorkQueues = []

class WorkItem:
    """Describes work to be done

    It takes a function to perform, and a queue to place itself in once work is complete
    """

    def __init__(self, taskFunc, RetQueue):
        self.Task = taskFunc	    # Worker function to be called
        self.RetQueue = RetQueue    # Queue in which to return this work item once complete
        self.ID = uuid.uuid4()      # Uniqueue identifier
        self.Status = 'Ready'       # Current status of work item (Ready, InProgress, Complete, Failed)
        self.Output = ""            # Output of command(s) in prometheus-friendly format
        self.Error = None           # Output of error if there's a problem running the task
        self.ExitCode = 0           # Exit code of the work item

    def Run(self):
        self.Status = 'InProgress'
        try:            
            self.Status = 'Complete'
            self.Output = self.Task()
            self.RetQueue.put(self)
            return
        except Exception as e:
            self.Status = 'Failed'
            self.Error = e.message
            self.ExitCode = 1            
            self.RetQueue.put(self)

    def IsComplete(self):
        return self.Status == 'Complete'

    def IsFailed(self):
        return self.Status == 'Failed'


class WorkCommander:
    """
    A class that takes a given work type that prepares and starts each script.
    Provided a list of functions to run, it will create work items and add them to the work queue.
    """

    def __init__(self, workFuncs):
        self.ID = uuid.uuid4()		# Uniqueue identifier
        self.QWork = Queue()
        self.QDisplay = Queue()
        self.WorkFuncs = workFuncs
        self.OutputString = ""

    def run(self):
        """Gathers work, performs it, then returns a webpage ready string of prometheus metrics"""

        logging.info("Commander "+self.ID+" started on the following functions: "+self.WorkFuncs)
        # Add our work to to the list of work queues
        ListWorkQueues.append(self.QWork)
        self.QueueUpWork()        
        # Wait until our work queue has been completed
        self.QWork.join()
        ListWorkQueues.remove(self.QWork)   # Now that our queue is complete we remove it from being checked for work
        self.ProcessCompletedWork()
        return self.OutputString

    def QueueUpWork(self):
        """ Adds it's work to the global work queue

        Fetches work for a given type, creates a WorkItem for each script, and places them in self.QWork
        Once there, the work will start being performed by workers monitoring the queue.
        """
        for func in self.WorkFuncs:
            self.QWork.put((WorkItem(func,self.QDisplay)))
        return

    def ProcessCompletedWork(self):
        """Takes the output of each work item and combines it for the webpage"""
        self.OutputString = ""
        # When a task is marked complete, it is also immediately placed in QDisplay
        # If QDisplay is empty, then there is no work left
        while not self.QDisplay.empty():
            try:
                workItem = self.QDisplay.get_nowait()
                self.OutputString = self.OutputString + workItem.Output + "\n"
                self.QDisplay.task_done()
            except:
                return
