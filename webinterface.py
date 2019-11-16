import comcommander as COM
import worker
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import threading

import TaskTypes.puppet as puppet
import TaskTypes.example_TT as example_TT

NUMWORKERS = 2  # Number of workers to create
ADDR = '127.0.0.1'
PORT = 9980  # Port to run the web interface on

TaskTypes = {}

def import_functions():
    scriptFiles = __import__("TaskTypes")
    for module in scriptFiles.keys:            
        listFuncs = getattr(module, "FuncList")
        TaskTypes[module.__name__] = listFuncs

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        print("recieved request")
        listFuncs = None
        exporter = self.path.replace('/','').lower()
        if exporter in TaskTypes:
            listFuncs = TaskTypes[exporter]
        else:
            listFuncs = TaskTypes["example_TT"]
        message = COM.WorkCommander(listFuncs).run()
        self.wfile.write(message)
        self.wfile.write('\n')
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""



if __name__ == '__main__':
    listWorkers = []
    for i in range(NUMWORKERS):
        thread = worker.threadWorker(COM.listWorkQueues)
        thread.start()
        listWorkers.append(thread)

    TaskTypes["example_TT"] = example_TT.FuncList

    TaskTypes["puppet"] = puppet.FuncList


    server = ThreadedHTTPServer((ADDR, PORT), Handler)
    print 'Starting server on '+ADDR+':'+str(PORT)+' , use <Ctrl-C> to stop'
    server.serve_forever()
