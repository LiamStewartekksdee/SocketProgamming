#!/usr/bin/env python3

import socket
import selectors
import types
# import ircserver
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

    # def joinchannel(self, user, channel):
    #     # channel = channel.lower()
    #     # user=user.lower()
    #     # channel.add(user)
    #     self.channels[channel]=self

    def join_channel(self, channelname):
        channel = self.server.get_channel(channelname)
        channel.add_member(self)
        self.channels[channelname.lower()] = channel
        print(" connected to " + channelname)
        print(self.channels)
        print(" are the client channels")
    
    def leave_channel(self, channelname):
        channel = self.channels[channelname.lower()]
        channel.remove_member(self)
        del self.channels[channelname.lower()]
        print(" left" + channelname)

