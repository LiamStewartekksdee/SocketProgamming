import chatbot
import socket
import selectors

class client:
    def __init__(self, botnick):
        self.botnick = botnick
        self.channels = set()
        self.serv_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sel = selectors.DefaultSelector()


    def __connect_client__(self, HOST, PORT):
        try:
            self.serv_conn.connect((HOST, PORT))
            self.serv_conn.setblocking(False)
            self.sel.register(self.serv_conn, selectors.EVENT_WRITE)
           
        except Exception as e:
            print(e)

    def run_client(self, HOST, PORT):
        maintain_conn = True
        self.__connect_client__(HOST, PORT)
        self.serv_conn.send(bytes("USER "+ self.botnick +" "+ self.botnick +" "+ self.botnick + " " + self.botnick + "\n", "UTF-8")) #We are basically filling out a form with this line and saying to set all the fields to the bot nickname.
        self.serv_conn.send(bytes("NICK "+ self.botnick +"\n", "UTF-8")) # assign the nick to the bot
            
        while maintain_conn:
            for key, mask in self.sel.select(timeout=1):
                try:
                    conn = key.fileobj
                    print('connecting to {}'.format(conn.getpeername()))
                    if mask and selectors.EVENT_WRITE:
                        data = input('{}:'.format(self.botnick)).encode()
                        conn.send(data)
                        print('recieved {!r}'.format(data))
                    else:
                        print('closing connection to ', key.data.addr)
                        self.sel.unregister(conn)
                        conn.close()

                except Exception as e:
                    print('closing ...')
                    self.sel.unregister(conn)
                    conn.close()
                    maintain_conn = False
                    #self.sel.close()

            
       
        #chatbot.run_bot(self.serv_conn)
    

if __name__ == '__main__':
    botnick_inp = input('Enter nickname: ')
    client = client(botnick_inp)
    client.run_client('localhost', 6667)