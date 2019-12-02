#!/usr/bin/env python3

import socket
import selectors
import types
import channel

class Client(object):
    def __init__(self, server, socket):
        self.server = server
        self.socket = socket
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
        # self.socket.send(bytes('332 ' + channelname + ' random topic', 'UTF-8'))
    
    def leave_channel(self, channelname):
        channel = self.channels[channelname.lower()]
        channel.remove_member(self)
        del self.channels[channelname.lower()]
        print(" left" + channelname)

    def leave_channels(self):
        for channel in self.channels.values():
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