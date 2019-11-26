#!/usr/bin/env python3

import socket
import selectors
import types

class Channel:
    def __init__(self, server, name):
        self.server = server
        self.name = name
        self.members = set()
        self.username = None
        self.realname = None
        self.nickname = None
    
    def add_member(self, client):
        self.members.add(client)
    
    def remove_member(self, client):
        self.members.discard(client)
        if not self.members:
            # remove channel - call server function, as it should deal with creating/deleting channels
            return
