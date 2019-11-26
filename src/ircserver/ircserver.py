import socket
import threading as th
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import chatbot


'''
Server based on the Internet Chat Relay(IRC) Protocol
'''
class ircserver:
    def __init__(self, server_address=('localhost', 6666)):
        # socket creation:
        # create socket, bind address, listen to connections, accept connections, send/receive data

        # family=AF_INET address family hat provides interprocess communication between processes that run on the same system/ different systems
        # type=SOCK_STREAM socket type that sends text in the same order as the original, delivery guaranteed
        self.server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.server_address = server_address

        # if the port is already in use reuse it 
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_socket.bind(self.server_address)
        self.server_socket.listen(10)
        self.sockets = [self.server_socket]

        # client fields, once connected to the client these fields will be set
        self.client_addr = None
        self.client_conn = None

        # bot initialiseation
        self.irc_bot = None

    def conn(self):
        # check if the socket is the server socket
        for so in self.sockets:
            if so.getsockname()[1] == self.server_address[1]:
                print('waiting for connection to the client')
                self.client_conn, client_addr = so.accept()
        
        self.create_bot('TESTBOT')
        while True:
            try:
                print('connection from {}'.format(client_addr))
                while True:
                    data = self.client_conn.recv(512)
                    print('received'.format(data))

                    self.irc_bot.ping()
                    if data:
                        self.client_conn.sendall(data)
                    else:
                        break
            except Exception as e:
                print(e)
                print('Closing the connection between the client and the server')
                self.client_conn.close()
                break


    # def create_channel(self, port):
    #     channel_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    #     channel_socket.bind((self.server_address[0], port))
    #     channel_socket.listen(10)
    #     self.sockets.append(channel_socket)

    
    def create_bot(self, botnick):
        # if self.irc_bot == None:
        #     raise Exception('Client not connected. Connect the client to create a bot')
        
        print('---Bot is connecting---')
        self.irc_bot = chatbot.irc_bot(self.client_conn, self.server_address, botnick)
        return self.irc_bot

    def get_server_info(self):
        return self.server_address, socket.gethostname()

    def get_server_socket(self):
        return self.server_socket
    
    def get_client_conn(self):
        if self.client_conn == None:
            raise Exception('Client not connected. Connect the client to use the client port')
        return self.client_conn

if __name__ == '__main__':
    ircserver = ircserver();
    ircserver.conn()
