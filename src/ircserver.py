#!/usr/bin/env python3

# Skeleton of IRC server handling multiple connections via https://realpython.com/python-sockets/#multi-connection-client-and-server

import socket
import selectors
import types
import client
import channel


class Server(object):
    def __init__(self):
        self.channels = {}
        self.clients = {}
        self.HOST = '127.0.0.1'
        self.PORT = 6667
        self.sel = selectors.DefaultSelector()

    def start(self):
        sel = selectors.DefaultSelector()
        # define server address
        HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
        # Port to listen on (non-privileged ports are > 1023)
        PORT = 6667

        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((HOST, PORT))
        lsock.listen()
        print('listening on', (HOST, PORT))
        # don't block when using socket, as we select from multiple sockets using selector
        lsock.setblocking(False)
        sel.register(lsock, selectors.EVENT_READ, data=None)

    def run(self):
        while True:
            # readlist, writelist, emptylist = select.select()
            events = self.sel.select(timeout=None)
            for key, mask in events:
                # if new connection, accept it using our wrapper function to create socket object and register it with the selector
                if key.data is None:
                    self.accept_wrapper(key.fileobj)
                # if it's been accepted, read or write or close
                else:
                    self.service_connection(key, mask)

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print('accepted connection from', addr)
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)
        
        self.clients[conn] = client.Client(self, conn)
        print("Accepted connection from %s:%s." % (addr[0], addr[1]))

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                data.outb += recv_data
            #     command, arguments = __parse_input(recv_data)
            #     if(command == "JOIN" & len(arguments)>0) joinchannel(,argument[0])
            else:
                print('closing connection to', data.addr)
                self.sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print('echoing', repr(data.outb), 'to', data.addr)
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    def get_channel(self, channelname):
        if channelname.lower() in self.channels:
            channel = self.channels[channelname.lower()]
        else:
            channel = channel.Channel(self, channelname)
            self.channels[channelname.lower()] = channel
        return channel
    
    def delete_channel(self, channel):
        del self.channels[channel.lower()]

    def remove_member_from_channel(self, client, channelname):
        if channelname.lower() in self.channels:
            channel = self.channels[channelname.lower()]
            channel.remove_member(client)
