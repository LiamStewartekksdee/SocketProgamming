#!/usr/bin/env python3

# Skeleton of IRC server handling multiple connections via https://realpython.com/python-sockets/#multi-connection-client-and-server

import socket
import selectors
import types
import client
import channel
import chatbot
import servererr as serr



class Server(object):
    def __init__(self):
        self.channels = {}
        self.clients = {}
        self.HOST = '127.0.0.1'
        self.PORT = 6667
        self.sel = selectors.DefaultSelector()
        #self.__registration_handler()

    def __registration_handler(self):
        command, arguments = self.__parse_input()
        if((command.upper() == "NICK") and len(arguments)>0):
            # set/change nickname
            #             #   Numeric Replies:

            #    ERR_NONICKNAMEGIVEN             ERR_ERRONEUSNICKNAME
            #    ERR_NICKNAMEINUSE               ERR_NICKCOLLISION

            has_nick = False
            if sock in self.clients:
                for client in self.clients.values():
                    if client.get_nickname() == arguments[0]:
                        sock.send(bytes('ERR_NICKNAMEINUSE code:' + str(serr.ERR_NICKNAMEINUSE), 'UTF-8'))
                        has_nick = True
                        break
                        
                if has_nick == False:
                    self.clients[sock].set_nickname(arguments[0])
                    sock.send(bytes('Nickname updated to ' + arguments[0] + '\n', 'UTF-8'))

        if(command.upper() == "USER"):
            # set/change username & realname <-- client has to take this step before registering
            #Parameters: <username> <hostname> <servername> <realname>
            has_username = False
            if sock in self.clients:
                for client in self.clients.values():
                    if client.get_username() == arguments[0]:
                        sock.send(bytes('ERR_USERNAMEINUSE code:' + str(serr.ERR_USERNAMEINUSE), 'UTF-8'))
                        has_username = True
                        break

                if has_username == False:
                    self.clients[sock].set_username(arguments[0])
                    sock.send(bytes('Username updated to ' + arguments[0] + '\n', 'UTF-8'))
                    has_logged = True
        
    
    def start(self):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((self.HOST, self.PORT))
        lsock.listen()
        print('listening on', (self.HOST, self.PORT))
        # don't block when using socket, as we select from multiple sockets using selector
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)

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
        # create a Client object and hold it in a dictionary as a pair socket : Client object
        self.clients[conn] = client.Client(self, conn)
        print("Accepted connection from %s:%s." % (addr[0], addr[1]))

        # for key, mask in self.sel.select(timeout=None):
        #     print(key)
    
    def __parse_input(self, line):
        x = line.split()
        command = x[0]
        arguments = x[1:]
        return command, arguments

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        has_logged = False
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024) # Should be ready to read
            if recv_data:
                data.outb += recv_data
                # parse the line provided by the user
                command, arguments = self.__parse_input(recv_data.decode('utf-8'))
                # if found 'join' command
                print("received data:")
                print(command)
                print(arguments)
                # we need at least 2 arguments - receiver and the message. Message is preceeded with colon
                if((command.upper() == "PRIVMSG") and len(arguments)>1):
                    # find out where to send the message and send it (pm or channel message)
                    pass
                if((command.upper() == "JOIN") and len(arguments)>0): 
                    # find the client in the dict searching for his socket
                    print("found join command and argument")
                    if sock in self.clients:
                        print("found client in dictionary")
                        # get client object that is in our dictionary as a 
                        # pair socket : Client object and connect Client to channel
                        print(arguments[0])
                        sock.send(bytes('332 ' + self.clients[sock].username + ' ' + arguments[0] + ' :random topic \r\n', 'UTF-8'))
                        sock.send(bytes('353 ' + self.clients[sock].username + ' username ' + arguments[0] + ' ' + self.clients[sock].username + ' 366 ' + self.clients[sock].username + ' ' + arguments[0] + ' :End of names list\r\n', 'UTF-8'))

                        self.clients[sock].join_channel(arguments[0])




                if((command.upper() == "PART") and len(arguments)>0):
                    # leave channel
                    if sock in self.clients:
                        if self.clients[sock].channels[arguments[0]]:
                            self.clients[sock].leave_channel(arguments[0])


                if(command.upper() == "USERS"):
                    for client in self.clients.values():
                        sock.send(bytes(str(client.get_username()) + '\n', 'UTF-8'))
                            
            else:
                print('closing connection to', data.addr)
                # leave channel before deleting socket
                self.clients[sock].leave_channels()
                # delete client from the dictionary
                if sock in self.clients: 
                    del self.clients[sock]
                # unregister and close socket made for a client
                self.sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                command, arguments = self.__parse_input(data.outb.decode('utf-8'))
                if((command.upper() == "PRIVMSG") and len(arguments)>0):
                    # targetname, message = self.__parse_input(arguments)
                    self.send_message(arguments[0], arguments[1:], sock)
                print('echoing', repr(data.outb), 'to', data.addr)
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    def get_channel(self, channelname):
        if channelname in self.channels:
            channel1 = self.channels[channelname.lower()]
        else:
            channel1 = channel.Channel(self, channelname)
            print(channelname + " channel created")
            self.channels[channelname.lower()] = channel1
        return channel1
    
    def delete_channel(self, channel):
        del self.channels[channel]

    def remove_member_from_channel(self, client, channelname):
        if channelname.lower() in self.channels:
            channel = self.channels[channelname.lower()]
            channel.remove_member(client)

    def send_message(self, targetname, message, sock):
        # targetname, message = self.__parse_input(line)
        for client in self.clients.values():
            if ((client.username == targetname) & (client != self.clients[sock])):
                # if (targetname in self.clients.values().username):
                if message:
                    sock.send(bytes(message, 'UTF-8'))
                    break
        if targetname in self.channels:
            self.send_message_to_channel(targetname, message, sock)

    
    def send_message_to_channel(self, channelname, message, sock):
        for member in self.channels[channelname.lower()].members:
            self.send_message(member, message, sock)
    

server = Server()
server.start()
server.run()