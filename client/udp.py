import os

BUFSIZE = 1024

def client_echo(sock, address, args):
    sock.sendto(' '.join(args).encode('ascii'), address)
    print(sock.recvfrom(BUFSIZE)[0].decode('ascii'), end='')

def client_time(sock, address, args):
    if len(args) != 1:
        print('usage: time')
        return

    sock.sendto(' '.join(args).encode('ascii'), address)
    print(sock.recvfrom(BUFSIZE)[0].decode('ascii'), end='')

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
            sock.sendto(int.to_bytes(i+1, length=4)+data, address)

            size += len(data)
            full_size = current_size+size

            if i % (2*BUFSIZE) == 0:
                print(f'{int(100*full_size/file_size):2d} %')

            i += 1

        sock.sendto(int.to_bytes(0, length=4)+bytes(BUFSIZE), address);

        print(f'transmitted {size:,.0f} bytes')
        print(f'uploaded \'{file_name}\'')

def client_download(sock, address, args):
    pass

def client_unknown(sock, address, args):
    sock.sendto(' '.join(args).encode('ascii'), address)
    print(sock.recvfrom(BUFSIZE)[0].decode('ascii'), end='')
