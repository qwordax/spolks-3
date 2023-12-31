import logging
import os
import random
import time

FATAL = False

last_address = None
last_file_name = None

BUFSIZE = 1024

def server_echo(sock, address, args):
    response = '\n'.join(args[1:])+'\n'
    sock.sendto(response.encode('ascii'), address)

def server_time(sock, address):
    response = time.ctime()+'\n'
    sock.sendto(response.encode('ascii'), address)

def server_upload(sock, address):
    global FATAL

    global last_address
    global last_file_name

    file_info = sock.recv(BUFSIZE).decode('ascii').split()

    file_name = file_info[0]
    file_size = int(file_info[1])

    is_continue = (last_address is not None and
                   last_address == address[0] and
                   last_file_name == file_name and
                   FATAL is True)

    if is_continue:
        current_size = os.path.getsize(file_name)
        file_mode = 'ab'
    else:
        current_size = 0
        file_mode = 'wb'

    sock.sendto(str(current_size).encode('ascii'), address)

    logging.info(f'uploading \'{file_name}\'')

    FATAL = False

    last_address = address[0]
    last_file_name = file_name

    i = 0
    size = 0

    with open(file_name, file_mode) as file:
        while True:
            data = sock.recv(BUFSIZE+4)

            index = int.from_bytes(data[:4], byteorder='big')
            data = data[4:]

            if index == 0:
                break

            if random.randint(0, 100) > 5:
                sock.sendto('ok'.encode('ascii'), address)
            else:
                sock.sendto('fail'.encode('ascii'), address)
                continue

            size += file.write(data)
            full_size = current_size+size

            if i % (2*BUFSIZE) == 0:
                logging.info(f'{int(100*full_size/file_size):2d} %')

            i += 1

    logging.info(f'received {size:,.0f} bytes')
    logging.info(f'uploaded \'{file_name}\'')

def server_download(sock, address, args):
    global FATAL

    global last_address
    global last_file_name

    if not os.path.exists(args[1]):
        sock.sendto('not exists'.encode('ascii'), address)
        return

    file_name = args[1]
    file_size = os.path.getsize(args[1])

    is_continue = (last_address is not None and
                   last_address == address[0] and
                   last_file_name == file_name and
                   FATAL is True)

    if is_continue:
        sock.sendto('continue'.encode('ascii'), address)
    else:
        sock.sendto('exists'.encode('ascii'), address)

    file_info = file_name+' '+str(file_size)
    sock.sendto(file_info.encode('ascii'), address)

    current_size = int(sock.recv(BUFSIZE).decode('ascii'))

    logging.info(f'downloading \'{file_name}\'')

    FATAL = False

    last_address = address[0]
    last_file_name = file_name

    with open(file_name, mode='rb') as file:
        file.seek(current_size)

        i = 0
        size = 0

        for data in iter(lambda: file.read(BUFSIZE), b''):
            while True:
                sock.sendto(int.to_bytes(
                    i+1,
                    byteorder='big',
                    length=4
                )+data, address)

                if sock.recv(BUFSIZE).decode('ascii') == 'ok':
                    break

            size += len(data)
            full_size = current_size+size

            if i % (2*BUFSIZE) == 0:
                logging.info(f'{int(100*full_size/file_size):2d} %')

            i += 1

    sock.sendto(int.to_bytes(
        0,
        byteorder='big',
        length=4
    )+bytes(BUFSIZE), address)

    logging.info(f'transmitted {size:,.0f} bytes')
    logging.info(f'downloaded \'{file_name}\'')

def server_unknown(sock, address, args):
    logging.error(f'unknown command \'{" ".join(args)}\'')

    response = f'error: unknown command \'{" ".join(args)}\'\n'
    sock.sendto(response.encode('ascii'), address)
