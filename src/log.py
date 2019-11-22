import logging
import datetime as dt

class log:
    def __init__(self, socket):
        self.socket = socket 
        self.write = logging.FileHandler('client_log.txt')

    def write_to_file(self):
        self.write

    def print_log(self):
        logging.warning('this is an error')

if __name__ == '__main__':
    import socket
    log = log(socket)
    log.print_log()
    log.write_to_file()