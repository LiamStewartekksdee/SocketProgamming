#!/usr/bin/env python3

import socket
import selectors
import types

class Client:
    def __init__(self, server, socket):
        self.server = server
        self.socket = socket
        # self.channels = {}
        self.channels = set()
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

    def joinchannel(self, user, channel):
        channel = channel.lower()
        user=user.lower()
        channel.add(user)
        self.channels.add(channel)
