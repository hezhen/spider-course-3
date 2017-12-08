import socket
import sys
from thread import *

class ServerSocket:
    # @param callback callback function for handling received data
    # @param host Symbolic name meaning all available interfaces
    # @param port Arbitrary non-privileged port
    def __init__(self, callback, host='localhost', port=20010):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.callback = callback

        #Bind socket to local host and port
        try:
            self.s.bind((host, port))
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

        # Start listening on socket
        self.s.listen(10)

    def startlistening(self):
        # now keep talking with the client
        while True:
            # wait to accept a connection - blocking call
            conn, addr = self.s.accept()

            #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
            start_new_thread(self.clientthread, (conn,))

    # Function for handling connections. This will be used to create threads
    def clientthread(self, conn):
        #Receiving from client
        data = conn.recv(1024)

        reply = self.callback(data)

        conn.sendall(reply)

        conn.close()


    def start(self):
        start_new_thread(self.startlistening, ())

    def close(self):
        # self.s.shutdown(socket.SHUT_WR)
        self.s.close()