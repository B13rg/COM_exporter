import comcommander as COM
import worker
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import threading

NUMWORKERS = 2  # Number of workers to create
ADDR = '127.0.0.1'
PORT = 9980  # Port to run the web interface on

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        print("recieved request")
        message = COM.WorkCommander(self.path).run()
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
    server = ThreadedHTTPServer((ADDR, PORT), Handler)
    print 'Starting server on '+ADDR+':'+str(PORT)+' , use <Ctrl-C> to stop'
    server.serve_forever()
