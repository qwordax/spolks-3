import os
import random

BUFSIZE = 1024

def client_echo(sock, address, args):
    sock.sendto(' '.join(args).encode('ascii'), address)
    print(sock.recv(BUFSIZE).decode('ascii'), end='')

def client_time(sock, address, args):
    if len(args) != 1:
        print('usage: time')
        return

    sock.sendto(' '.join(args).encode('ascii'), address)
    print(sock.recv(BUFSIZE).decode('ascii'), end='')

def client_upload(sock, address, args):
    if len(args) != 2:
        print('usage: upload <file>')
        return

    if not os.path.exists(args[1]):
        print(f'error: \'{args[1]}\' does not exists')
        return

    sock.sendto(' '.join(args).encode('ascii'), address)

    file_name = args[1]
    file_size = os.path.getsize(args[1])

    file_info = file_name+' '+str(file_size)
    sock.sendto(file_info.encode('ascii'), address)

    current_size = int(sock.recv(BUFSIZE).decode('ascii'))

    print(f'uploading \'{file_name}\'')

    with open(file_name, 'rb') as file:
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
                print(f'{int(100*full_size/file_size):2d} %')

            i += 1

    sock.sendto(int.to_bytes(
        0,
        byteorder='big',
        length=4
    )+bytes(BUFSIZE), address)

    print(f'transmitted {size:,.0f} bytes')
    print(f'uploaded \'{file_name}\'')

def client_download(sock, address, args):
    if len(args) != 2:
        print('usage: download <file>')
        return

    sock.sendto(' '.join(args).encode('ascii'), address)
    response = sock.recv(BUFSIZE).decode('ascii')

    if response == 'not exists':
        print(f'error: \'{args[1]}\' does not exists')
        return

    is_continue = response == 'continue'

    file_info = sock.recv(BUFSIZE).decode('ascii').split()

    file_name = file_info[0]
    file_size = int(file_info[1])

    if is_continue:
        current_size = os.path.getsize(file_name)
        file_mode = 'ab'
    else:
        current_size = 0
        file_mode = 'wb'

    sock.sendto(str(current_size).encode('ascii'), address)

    print(f'downloading \'{file_name}\'')

    i = 0
    size = 0

    with open(file_name, file_mode) as file:
        while True:
            data = sock.recv(BUFSIZE+4)

            index = int.from_bytes(data[:4], byteorder='big')
            data = data[4:]

            if index == 0:
                break

            size += file.write(data)
            full_size = current_size+size

            if random.randint(0, 100) > 5:
                sock.sendto('ok'.encode('ascii'), address)
            else:
                sock.sendto('fail'.encode('ascii'), address)
                continue

            if i % (2*BUFSIZE) == 0:
                print(f'{int(100*full_size/file_size):3d} %')

            i += 1

    print(f'received {size:,.0f} bytes')
    print(f'downloaded \'{file_name}\'')

def client_unknown(sock, address, args):
    sock.sendto(' '.join(args).encode('ascii'), address)
    print(sock.recv(BUFSIZE).decode('ascii'), end='')
