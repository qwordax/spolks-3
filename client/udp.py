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
    pass

def client_download(sock, address, args):
    pass

def client_unknown(sock, address, args):
    sock.sendto(' '.join(args).encode('ascii'), address)
    print(sock.recvfrom(BUFSIZE)[0].decode('ascii'), end='')
