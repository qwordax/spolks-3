import logging
import os
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

    file_dict = dict()

    while True:
        data = sock.recv(BUFSIZE+4)

        index = int.from_bytes(data[:4])
        data = data[4:]

        if index == 0:
            break

        file_dict[index] = data

        size += len(data)
        full_size = current_size+size

        if i % (2*BUFSIZE) == 0:
            logging.info(f'{int(100*full_size/file_size):2d} %')

        i += 1

    with open(file_name, file_mode) as file:
        for _, data in sorted(file_dict.items()):
            file.write(data)

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

    file_info = file_name + ' ' + str(file_size)
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
            sock.sendto(int.to_bytes(i+1, length=4)+data, address)

            size += len(data)
            full_size = current_size+size

            if i % (2*BUFSIZE) == 0:
                logging.info(f'{int(100*full_size/file_size):2d} %')

            i += 1

    sock.sendto(int.to_bytes(0, length=4)+bytes(BUFSIZE), address)

    logging.info(f'transmitted {size:,.0f} bytes')
    logging.info(f'downloaded \'{file_name}\'')

def server_unknown(sock, address, args):
    logging.error(f'unknown command \'{" ".join(args)}\'')

    response = f'error: unknown command \'{" ".join(args)}\'\n'
    sock.sendto(response.encode('ascii'), address)
