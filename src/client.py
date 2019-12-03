#!/usr/bin/env python3

import socket
import selectors
import types
import channel

class Client():
    def __init__(self, server, socket):
        self.server = server
        self.socket = socket
        self.host = socket.getpeername()
        self.channels = {}
        self.username = None
        self.realname = None
        self.nickname = None
        self.readbuffer = ""
        self.writebuffer = ""
    
    def __parse_input(self, line):
        x = line.split()
        command = x[0]
        arguments = [x[1:]]
        return command, arguments

    def join_channel(self, channelname):
        channel = self.server.get_channel(channelname)
        channel.add_member(self)
        self.channels[channelname.lower()] = channel
        print(" connected to " + channelname)
        print(self.channels)
        print(" are the client's channels")

        print(self.server.get_key().fileobj)
        
        response_format = ':%s TOPIC %s :%s\r\n' % (channel.topic_by, channel.name, channel.topic)
        self.writebuffer += response_format
        
        response_format = ':%s JOIN :%s\r\n' % (self.server.get_prefix() % (self.nickname, self.username, self.server.HOST), channelname)
        self.writebuffer += response_format

        clients = self.server.get_clients()
        nicks = [client.get_nickname() for client in clients.values()]
        
        response_format = ':%s 353 %s = %s :%s\r\n' % (self.server.HOST, self.nickname, channelname, ' '.join(nicks))
        self.writebuffer += response_format
    
        response_format = ':%s 366 %s %s: End of /NAMES list\r\n' % (self.server.HOST, self.nickname, channelname)
        self.writebuffer += response_format

        self.server.send_message_to_client(self.writebuffer, key=self.server.get_key())
        self.writebuffer = ""

    def leave_channel(self, channelname):
        channel = self.channels[channelname.lower()]
    
    def msg_chann(self, command, message):
        msg_format = ':%s %s %s' % (self.prefix, command, argument)   
        channel.remove_member(self)
        del self.channels[channelname.lower()]
        print(" left" + channelname)

    def leave_channels(self):
        for channel in self.channels:
            channel.remove_member(self)
            del channel
    
    def set_nickname(self, nickname):
        self.nickname = nickname

    def get_nickname(self):
        return self.nickname

    def set_username(self, username):
        self.username = username

    def get_username(self):
        return self.username

    def get_host(self):
        return self.host