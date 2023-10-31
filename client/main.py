import socket
import sys

import tcp
import udp

def handle_tcp(sock):
    while True:
        args = input('> ').split()

        if args == []:
            continue

        try:
            if args[0] == 'close' or args[0] == 'exit' or args[0] == 'quit':
                sock.send(' '.join(args).encode('ascii'))
                break

            if args[0] == 'echo':
                tcp.client_echo(sock, args)
            elif args[0] == 'time':
                tcp.client_time(sock, args)
            elif args[0] == 'upload':
                tcp.client_upload(sock, args)
            elif args[0] == 'download':
                tcp.client_download(sock, args)
            else:
                tcp.client_unknown(sock, args)
        except ConnectionAbortedError:
            print('error: connection aborted')
            break
        except ConnectionResetError:
            print('error: connection reset')
            break
        except TimeoutError:
            print('error: timeout')
            break

def handle_udp(sock, address):
    while True:
        args = input('> ').split()

        if args == []:
            continue

        try:
            if args[0] == 'close' or args[0] == 'exit' or args[0] == 'quit':
                sock.sendto(' '.join(args).encode('ascii'), address)
                break

            if args[0] == 'echo':
                udp.client_echo(sock, address, args)
            elif args[0] == 'time':
                udp.client_time(sock, address, args)
            elif args[0] == 'upload':
                udp.client_upload(sock, address, args)
            elif args[0] == 'download':
                udp.client_download(sock, address, args)
            else:
                udp.client_unknown(sock, address, args)
        except ConnectionAbortedError:
            print('error: connection aborted')
            break
        except ConnectionResetError:
            print('error: connection reset')
            break
        except TimeoutError:
            print('error: timeout')
            break

def main():
    if len(sys.argv) != 4:
        print('usage: %s {tcp|udp} <address> <port>' % sys.argv[0])
        return

    protocol = sys.argv[1]
    address = (sys.argv[2], int(sys.argv[3]))

    socket.setdefaulttimeout(30)

    if protocol == 'tcp':
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect(address)
        except TimeoutError:
            print('error: timed out'); sock.close()
            return
    elif protocol == 'udp':
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        print(f'error: unknown protocol \'{protocol}\'')
        return

    if protocol == 'tcp':
        handle_tcp(sock)
    else:
        handle_udp(sock, address)

    sock.close()

if __name__ == "__main__":
    main()
