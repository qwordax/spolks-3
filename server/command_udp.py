import logging
import time

FATAL = False

last_address = None
last_file_name = None

BUFSIZE = 1024

def server_echo(sock, address, args):
    response = '\n'.join(args[1:]) + '\n'
    sock.sendto(response.encode('ascii'), address)

def server_time(sock, address):
    response = time.ctime() + '\n'
    sock.sendto(response.encode('ascii'), address)

def server_upload(sock, address):
    pass

def server_download(sock, address, args):
    pass

def server_unknown(sock, address, args):
    logging.error(f'unknown command \'{" ".join(args)}\'')

    response = f'error: unknown command \'{" ".join(args)}\'\n'
    sock.sendto(response.encode('ascii'), address)
