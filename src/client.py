#!/usr/bin/env python3

import socket
import selectors
import types
import channel
import servererr as serr


'''
This class handles all the commands for the client/bot that connects to the server
'''
class Client():
    '''
    we need the server object to call certian server methods and the clients socket to send events
    '''
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
        self.key = None


    '''
    Handles when a user first loggs in
    '''
    def __registration_handler(self, key, command, arguments):
        sock = key.fileobj
        data = key.data
        
        # handle the /NICK command and the /USER command
        self.__nickname_handler(key, command, arguments)
        self.__username_handler(key, command, arguments)
        

        if self.username is not None and self.nickname is not None:
            # change the handler to command handler so the user can use commands such as /JOIN
            self.handler = self.__command_handler
            self.prefix % (self.nickname, self.username, self.server.HOST)
            self.welcome_message(key)

            # if not self.has_joined_channel('#test'):
            #     self.__join_handler(key, 'JOIN', ['#test'])
        else:
            # if registration is not successful then the handler stays as the registration handler
            if data:
                self.handler = self.__registration_handler

    '''
    sets the nickname of the client
    '''
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
                        
                
                if not self.nickname or not has_nick:
                    self.nickname = arguments[0]
                    sock.send(bytes('Nickname updated to ' + arguments[0] + '\n', 'UTF-8'))
                
                # # updating the nickname
                # if self.nickname is not None and not has_nick:
                #     self.nickname = arguments[0]
                #     response_format = ':%s %s %s\r\n' % (self.server.HOST, '001', self.nickname)
                #     self.writebuffer += response_format
                #     response_format = ':%s 376 %s :End of command, NICK updated.' % (self.server.HOST, self.nickname)
                #     self.writebuffer += response_format
                #     self.server.send_message_to_client(self.writebuffer, key)
                #     self.writebuffer = ""
                        
                    
    '''
    sets the username of the client
    '''
    def __username_handler(self, key, command, arguments):
        sock = key.fileobj
        # this makes sure that the user is set when the client first signs up 
        if len(arguments) > 1 and arguments[1] == "USER":
            command = arguments[1]
            arguments[0] = arguments[2]
        
        if(command.upper() == "USER"):

            has_username = False
            # checks if the username is in use
            if sock in self.server.clients:
                for client in self.server.clients.values():
                    if client.get_username() == arguments[0]:
                        sock.send(bytes('ERR_USERNAMEINUSE code:' + str(serr.ERR_USERNAMEINUSE), 'UTF-8'))
                        has_username = True
                        break

                if not self.username or not has_username:
                    self.username = arguments[0]
                    sock.send(bytes('Username updated to ' + arguments[0] + '\n', 'UTF-8'))

                # if self.username is not None and not has_username:
                #     response_format = ':%s %s %s\r\n' % (self.server.HOST, '001', self.username)
                #     self.writebuffer += response_format
                #     response_format = ':%s 376 %s :End of command.' % (self.server.HOST, self.username)
                #     self.writebuffer += response_format
                #     self.server.send_message_to_client(self.writebuffer, key)
                #     self.writebuffer = ""

    '''
    lists all the users connected
    '''
    def __users_handler(self, key, command, arguments):
        sock = key.fileobj
        if(command.upper() == "USERS"):
            for client in self.server.clients.values():
                sock.send(bytes(str(client.get_username()) + '\n', 'UTF-8'))
    

    '''
    join a client into a channel
    '''
    def __join_handler(self, key, command, arguments):
        sock = key.fileobj
        data = key.data
        if((command.upper() == "JOIN") and len(arguments)>0): 
            # find the client in the dict searching for his socket
            print("found join command and argument")
            if sock in self.server.clients:
                print("found client in dictionary")
                print(arguments[0])
                self.join_channel(key, arguments[0])
    
    '''
    when a client leaves a channel
    '''
    def __part_handler(self, key, command, arguments):
        sock = key.fileobj
        if((command.upper() == "PART") and len(arguments)>0):
            # leave channel
            if sock in self.server.clients:
                self.leave_channel(key, arguments[0])


    '''
    PRIVMSG a channel or a user. This method checks for this and handles appropiately
    '''
    def __privmsg_handler(self, key, command, arguments):
        if((command.upper() == "PRIVMSG") and len(arguments)>1):
            target = arguments[0]

            message = arguments[1:]
            print(arguments)
            #:source PRIVMSG <target> :Message
            # format to be sent back to the client
            response_format = ':%s PRIVMSG %s %s\n' % (self.prefix % (self.nickname, self.username, self.server.HOST), target, ' '.join(message))
            
            # checks if the target is a channel
            has_channel = self.server.has_channel(target)
            if has_channel:
                channel = self.server.get_channel(target)
                for client in channel.members:
                    if client is not self:
                        client.writebuffer += response_format
                        # sends to the client socket so all the other clients can view the message   
                        self.server.send_message_to_client(client.writebuffer, client.key)
                        print(client.key)

                 # free the write buffer
                for client in channel.members:
                    client.writebuffer = ""
            else:
                # otherwise the message is intended for a specific user
                for client in self.server.clients.values():
                    if client.get_nickname() == target:
                        client.writebuffer += response_format
                        # sends to the client socket so all the other clients can view the message
                        self.server.send_message_to_client(client.writebuffer, client.key)

                # free the write buffer
                for client in self.server.clients.values():
                    if client.get_nickname() == target:
                        client.writebuffer = ""

    '''
    Where the commands are handled
    '''    
    def __command_handler(self, key, command, arguments):
        self.__nickname_handler(key, command, arguments)
        self.__username_handler(key, command, arguments)
        self.__join_handler(key, command, arguments)
        self.__part_handler(key, command, arguments)
        self.__users_handler(key, command, arguments)
        self.__privmsg_handler(key, command, arguments)


    '''
    Main join functionality called in __join_handler
    '''
    def join_channel(self, key, channelname):
        channel = self.server.get_channel(channelname)
        channel.add_member(self)
        self.channels[channelname.lower()] = channel
        print(" connected to " + channelname)
        print(self.channels)
        print(" are the client's channels")

        ##
        # Format to be sent
        # different events such as TOPIC, JOIN, NAMES list is sent. Then the channel is created
        ##
        response_format = ':%s TOPIC %s :%s\r\n' % (channel.topic_by, channel.name, channel.topic)
        self.writebuffer += response_format

        for client in self.server.clients.values():      
            response_format = ':%s JOIN :%s\r\n' % (self.prefix % (client.nickname, client.username, client.server.HOST), channelname)
            self.writebuffer += response_format

        clients = self.server.get_clients()
        nicks = [client.get_nickname() for client in clients.values()]

        response_format = ':%s 353 %s = %s :%s\r\n' % (self.server.HOST, self.nickname, channelname, ' '.join(nicks))
        self.writebuffer += response_format
    
        response_format = ':%s 366 %s %s: End of /NAMES list\r\n' % (self.server.HOST, self.nickname, channelname)
        self.writebuffer += response_format

        # server sends the message
        self.server.send_message_to_client(self.writebuffer, key=key)
        self.writebuffer = ""


    '''
    Main part functionality called in __part_handler
    '''
    def leave_channel(self, key, channelname):
        channel = self.channels[channelname.lower()]
        channel.remove_member(self)

        # Format to be sent, the event part is sent to make sure the client has left th channel
        self.writebuffer += ':%s PART :%s\r\n' % (self.prefix % (self.nickname, self.username, self.server.HOST), channelname)
        self.server.send_message_to_client(self.writebuffer, key=key)
        self.writebuffer = ""

    '''
    When a client leaves remove them from the channels
    '''
    def leave_channels(self):
        for channel in self.channels.values():
            channel.remove_member(self)
            del channel
    

    '''
    Welcome message when the client registers
    '''
    def welcome_message(self, key):
        sock = key.fileobj
        divider = '----------------------------'

        sock.send(bytes(divider + '\r\n', 'UTF-8'))
        sock.send(bytes('Welcome to @' + self.server.HOST + '\r\n', 'UTF-8'))
        sock.send(bytes(divider + '\r\n', 'UTF-8'))
        sock.send(bytes('USER: ' + self.nickname + ' NICK: ' + self.username + '\r\n', 'UTF-8'))
        sock.send(bytes('Use /JOIN <#channelname> to join a channel and chat' + '\r\n', 'UTF-8'))
        sock.send(bytes('Use /HELP to list the available commands' + '\r\n', 'UTF-8'))
        sock.send(bytes(divider + '\r\n', 'UTF-8'))

    '''
    checks if the client has joined a channel
    '''
    def has_joined_channel(self, channelname):
        if channelname.lower() in self.channels:
            return True

    '''
    setters and getters
    '''
    def set_nickname(self, nickname):
        self.nickname = nickname

    def get_nickname(self):
        return self.nickname

    def set_username(self, username):
        self.username = username

    def get_username(self):
        return self.username