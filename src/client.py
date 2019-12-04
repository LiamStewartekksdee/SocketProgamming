#!/usr/bin/env python3

import socket
import selectors
import types
import channel
import servererr as serr

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
        self.prefix = '%s!%s@%s' #nickname, user, host
        self.handler = self.__registration_handler
    
    def __parse_input(self, line):
        x = line.split()
        command = x[0]
        arguments = [x[1:]]
        return command, arguments

    def __registration_handler(self, key, command, arguments):
        sock = key.fileobj
        data = key.data
        sock.send(bytes('Use /USER <name>  and /NICK <name> to register. Once registered you can use commands\n', 'UTF-8'))
        
        # handle the /NICK command and the /USER command
        self.__nickname_handler(key, command, arguments)
        self.__username_handler(key, command, arguments)
        

        if self.username is not None and self.nickname is not None:
            self.handler = self.__command_handler
            self.prefix % (self.nickname, self.username, self.server.HOST)
            sock.send(bytes('Registered! You can now use commands \n', 'UTF-8'))
        else:
            if data:
                self.handler = self.__registration_handler

    def __nickname_handler(self, key, command, arguments):
        sock = key.fileobj
    
        if((command.upper() == "NICK") and len(arguments)>0):
            has_nick = False
            if sock in self.server.clients:
                for client in self.server.clients.values():
                    if client.get_nickname() == arguments[0]:
                        sock.send(bytes('ERR_NICKNAMEINUSE code:' + str(serr.ERR_NICKNAMEINUSE), 'UTF-8'))
                        has_nick = True
                        break
                        
                if has_nick == False:
                    self.nickname = arguments[0]
                    sock.send(bytes('Nickname updated to ' + arguments[0] + '\n', 'UTF-8'))

    def __username_handler(self, key, command, arguments):
        sock = key.fileobj
        if(command.upper() == "USER"):
            # set/change username & realname <-- client has to take this step before registering
            #Parameters: <username> <hostname> <servername> <realname>
            has_username = False
            if sock in self.server.clients:
                for client in self.server.clients.values():
                    if client.get_username() == arguments[0]:
                        sock.send(bytes('ERR_USERNAMEINUSE code:' + str(serr.ERR_USERNAMEINUSE), 'UTF-8'))
                        has_username = True
                        break

                if has_username == False:
                    self.username = arguments[0]
                    sock.send(bytes('Username updated to ' + arguments[0] + '\n', 'UTF-8'))
                    has_logged = True


    def __users_handler(self, key, command, arguments):
        sock = key.fileobj
        if(command.upper() == "USERS"):
            for client in self.server.clients.values():
                sock.send(bytes(str(client.get_username()) + '\n', 'UTF-8'))
    

    def __join_handler(self, key, command, arguments):
        sock = key.fileobj
        data = key.data
        if((command.upper() == "JOIN") and len(arguments)>0): 
            # find the client in the dict searching for his socket
            print("found join command and argument")
            if sock in self.server.clients:
                print("found client in dictionary")
                # get client object that is in our dictionary as a 
                # pair socket : Client object and connect Client to channel
                print(arguments[0])
                self.join_channel(key, arguments[0])
                #send_format = "TOPIC %s :%s" % (self.channels[arguments[0]].get_channel_name(), self.channels[arguments[0]].get_topic())
                
                #data.inb = send_format
    
    def __part_handler(self, key, command, arguments):
        if((command.upper() == "PART") and len(arguments)>0):
            # leave channel
            if sock in self.server.clients:
                if self.server.clients[sock].channels[arguments[0]]:
                    self.server.clients[sock].leave_channel(arguments[0])
    

    def __privmsg_handler(self, key, command, arguments):
        if((command.upper() == "PRIVMSG") and len(arguments)>1):
            # find out where to send the message and send it (pm or channel message)
            pass
    
    def __command_handler(self, key, command, arguments):
        self.__nickname_handler(key, command, arguments)
        self.__username_handler(key, command, arguments)
        self.__join_handler(key, command, arguments)
        self.__part_handler(key, command, arguments)
        self.__users_handler(key, command, arguments)
        self.__privmsg_handler(key, command, arguments)


    def join_channel(self, key, channelname):
        channel = self.server.get_channel(channelname)
        channel.add_member(self)
        self.channels[channelname.lower()] = channel
        print(" connected to " + channelname)
        print(self.channels)
        print(" are the client's channels")
    
        
        response_format = ':%s TOPIC %s :%s\r\n' % (channel.topic_by, channel.name, channel.topic)
        self.writebuffer += response_format
        
        response_format = ':%s JOIN :%s\r\n' % (self.prefix % (self.nickname, self.username, self.server.HOST), channelname)
        self.writebuffer += response_format

        clients = self.server.get_clients()
        nicks = [client.get_nickname() for client in clients.values()]
        
        response_format = ':%s 353 %s = %s :%s\r\n' % (self.server.HOST, self.nickname, channelname, ' '.join(nicks))
        self.writebuffer += response_format
    
        response_format = ':%s 366 %s %s: End of /NAMES list\r\n' % (self.server.HOST, self.nickname, channelname)
        self.writebuffer += response_format

        self.server.send_message_to_client(self.writebuffer, key=key)
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
