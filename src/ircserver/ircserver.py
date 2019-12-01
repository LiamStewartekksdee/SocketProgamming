#!/usr/bin/env python3

# Skeleton of IRC server handling multiple connections via https://realpython.com/python-sockets/#multi-connection-client-and-server

import socket
import selectors
import types
import threading
from queue import Queue



class Server():
    def __init__(self):
        self.NUM_THREADS = 2
        self.JOB_NUM = [1, 2, 3]  
        self.queue = Queue()
        self.channels = {}
        self.threads = []
        self.registers = []

        self.HOST = 'localhost'
        self.PORT = 6667
        self.sel = selectors.DefaultSelector()

        self.create_threads()
        self.init_jobs()
        #self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.channels['localhost'] = self.server_sock

        

    def start(self, sock, event_type, HOST, PORT):
        sock.bind((HOST, PORT))
        sock.listen(10)
        print('listening on', (HOST, PORT))
        # don't block when using socket, as we select from multiple sockets using selector
        sock.setblocking(False)
        self.registers.append(self.sel.register(sock, event_type, data=None))

        for key, mask in self.sel.select(timeout=None):
            print('key: {0}, mask: {1}'.format(key, mask))

    def create_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return sock

    def accept_conn(self):
        while True:
            events = self.sel.select(timeout=None)
            for key, mask in events:
                #print('{0}, {1}'.format(key, mask))
                # if new connection, accept it using our wrapper function to create socket object and register it with the selector
                if key.data is None:
                    self.accept_wrapper(key.fileobj)
                # if it's been accepted, read or write or close
                else:
                    self.service_connection(key, mask)
            
    def accept_wrapper(self, sock):
        print('Waiting for connection to the client ... ')
        conn, addr = sock.accept()  # Should be ready to read
        print('accepted connection from', addr)
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            print(recv_data)
            if recv_data:
                data.outb += recv_data

            #     command, arguments = __parse_input(recv_data)
            #     if(command == "JOIN" & len(arguments)>0) joinchannel(,argument[0])
            else:
                print('closing connection to ', data.addr)
                self.sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print('echoing', repr(data.outb), 'to', data.addr)
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

                # if repr(data.outb).find('nJOIN #testchannel'):
                #     if '#testchannel' not in self.channels:
                #         print('creating test channel...')
                #         sock = self.create_sock()
                #         self.channels['#testchannel'] = sock
                #         self.start(sock, selectors.EVENT_READ, self.HOST, self.PORT+1)
                

    def run(self):
        while True:
            j_num = self.queue.get()
            if j_num == 1:
                self.start(self.create_sock(), selectors.EVENT_READ, self.HOST, self.PORT)
                self.accept_conn()
            # if j_num == 2:
            #     self.start(self.create_sock(), selectors.EVENT_READ, self.HOST, 6668)
            
            # if j_num == 3:
            #     self.accept_conn()  

                #self.accept_conn()

            
            self.queue.task_done()

    def create_threads(self):
        for i in range(self.NUM_THREADS):
            t = threading.Thread(target=self.run)
            t.daemon = True
            t.start()
            self.threads.append(t)
                
    def init_jobs(self):
        for i in self.JOB_NUM:
            self.queue.put(i)

        self.queue.join()      

if __name__ == '__main__':
    ircserver = Server()

    # #simple server
    # HOST = 'localhost'
    # PORT = 7000
    # sel = selectors.DefaultSelector()

    # serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # serv_socket.bind((HOST, PORT))
    # serv_socket.listen(10)
    # serv_socket.setblocking(False)

    # sel.register(serv_socket, selectors.EVENT_READ | selectors.EVENT_WRITE)

    # while True:
    #     for key, mask in sel.select(timeout=1):
    #         conn = key.fileobj
    #         print('client {}'.format(conn.getpeername()))

    #         if mask and selectors.EVENT_READ:
    #             print('ready to read')
    #             data = conn.recv(512)
    #             if data:
    #                 print('recieved {!r}'.format(data))
            
    #         if mask and selectors.EVENT_WRITE:
    #             print('ready to write')

