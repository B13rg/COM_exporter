import argparse
import logging
import pkgutil
import sys
import threading
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn

import comcommander as COM
import worker

NUMWORKERS = 2  # Number of workers to create
ADDR = '127.0.0.1'
PORT = 9980  # Port to run the web interface on
TASKDIR = './TaskTypes' # Location of various task scripts
LOGDIR = 'COM_exporter.log'

TaskTypes = {}  # Dictionary of all of our different task types and their corresponding function sets

def configureLogging():
    logging.basicConfig(
    filename=LOGDIR,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)

def parseArguments():
    """Setup argument parsing"""

    # Make our global 
    global NUMWORKERS, ADDR, PORT, TASKDIR, LOGDIR
    parser = argparse.ArgumentParser(description='Runs `puppet agent -t` command on remote hosts')
    parser.add_argument('-d', '--hostname', help="Address the exporter is running under.  Default: "+str(ADDR))
    parser.add_argument('-l', '--log', help="Path and filename where the logfile is stored. Default: "+str(LOGDIR))
    parser.add_argument('-p', '--port', type=int, help="Port the exporter runs under.  Default: "+str(PORT))
    parser.add_argument('-t', '--taskdir', help="Directory where Task configurations are stored. Default: "+str(TASKDIR))
    parser.add_argument('-w', '--workers', type=int, help="Number of workers to create to do work.  Default: "+str(NUMWORKERS))
    arguments = parser.parse_args()
    if arguments.log != None:
        LOGDIR = arguments.log
    # Have to configure the logging before we begin logging
    configureLogging()
    # Display arguments passed in for debugging
    logging.info("Received the following arguments: "+arguments)

    # Apply our arguments to variables
    if arguments.hostname != None:
        ADDR = arguments.hostname
    if arguments.port != None:
        PORT = arguments.port
    if arguments.hostname != None:
        TASKDIR = arguments.taskdir
    if arguments.hostname != None:
        NUMWORKERS = arguments.workers


def load_all_modules(dirname):
    """Loads all python modules and stores their FuncLists in the TaskTypes dict
    
    It will go through each file in the given directory, and attempt to load the module.
    If the module has a FuncList variable, it will be added to the TaskTypes dict with the module name as the key
    """

    for importer, package_name, _ in pkgutil.iter_modules([dirname]):
        full_package_name = '%s.%s' % (dirname, package_name)
        if full_package_name not in sys.modules:
            module = importer.find_module(
                package_name).load_module(package_name)
            if module.FuncList:
                # To run this funclist, you'll need to navigate to http://url:port/<module.__name__>
                TaskTypes[module.__name__] = module.FuncList
            print('Loaded module '+module.__name__)
            logging.info('Loaded module '+module.__name__)


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Immediately send our response headers, we have 10 seconds to respond
        self.send_response(200)
        self.end_headers()
        print("Received request from "+self.address_string()+" for "+self.path)
        logging.info("Request from "+self.address_string()+" for "+self.path)   # Log the request
        exporter = self.path.replace('/', '').lower()
        # Try to fetch the TaskType and run it's funcs
        if exporter in TaskTypes:
            listFuncs = TaskTypes[exporter]
            message = COM.WorkCommander(listFuncs).run()
        else:
            # If the TaskType doesn't exist, write a 404 message
            message = self.not_Found()
        self.wfile.write(message)
        self.wfile.write('\n')
        return

    def not_Found(self):
        return "404"


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Enables us to handle each request in a separate thread."""


if __name__ == '__main__':
    parseArguments()    # Sets up global variables
    # Create our workers and start them
    listWorkers = []
    for i in range(NUMWORKERS):
        thread = worker.threadWorker(COM.ListWorkQueues)
        thread.daemon = True    # Stops python from waiting on these to exit
        thread.start()
        listWorkers.append(thread)
    # Import the different scripts from our task directory
    load_all_modules(TASKDIR)
    # Start the web server
    server = ThreadedHTTPServer((ADDR, PORT), Handler)
    logging.info('Starting server on '+ADDR+':'+str(PORT))
    print 'Starting server on '+ADDR+':'+str(PORT)+' , use <Ctrl-C> to stop'
    server.serve_forever()  # or until we're killed
