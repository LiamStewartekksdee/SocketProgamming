import socket

'''
Server based on the Internet Chat Relay(IRC) Protocol
'''
class ircserver:
    def __init__(self, server_address=('localhost', 6000)):
        # socket creation:
        # create socket, bind address, listen to connections, accept connections, send/receive data

        # family=AF_INET address family hat provides interprocess communication between processes that run on the same system/ different systems
        # type=SOCK_STREAM socket type that sends text in the same order as the original, delivery guaranteed
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.server_address = server_address
        
        self.socket.bind(self.server_address)
        self.socket.listen(10)



    def conn(self):
        while True:
            # Wait for a connection
            print('waiting for a connection')
            connection, client_address = self.socket.accept()
            try:
                print('connection from', client_address)

                # Receive the data in small chunks and retransmit it
                while True:
                    data = connection.recv(512)
                    print('received {!r}'.format(data))
                    if data:
                        print('sending data back to the client')
                        connection.sendall(data)
                    else:
                        print('no data from', client_address)
                        break

            except Exception as e:
                # Clean up the connection
                print("Closing current connection")
                print(e)
                connection.close()

    def create_channel(self):
        pass

if __name__ == '__main__':
    ircserver = ircserver();
    ircserver.conn()
