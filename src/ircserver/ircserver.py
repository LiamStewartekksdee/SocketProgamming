#!/usr/bin/env python3

# Skeleton of IRC server handling multiple connections via https://realpython.com/python-sockets/#multi-connection-client-and-server

import socket
import selectors
import types

channels = set()

sel = selectors.DefaultSelector()
# define server address
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 6667        # Port to listen on (non-privileged ports are > 1023)

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
print('listening on', (HOST, PORT))
# don't block when using socket, as we select from multiple sockets using selector
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        # if new connection, accept it using our wrapper function to create socket object and register it with the selector
        if key.data is None:
            accept_wrapper(key.fileobj)
        # if it's been accepted, read or write or close
        else:
            service_connection(key, mask)

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print('echoing', repr(data.outb), 'to', data.addr)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

def joinchannel(user, channel):
    channel = channel.lower()
    user=user.lower()
    channel.add(user)
    channels.add(channel)

def __parse_input(line):
    x = line.split()
    command = x[0]
    arguments = [x[1:]]
    return command, arguments

