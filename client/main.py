import socket
import sys

import command_tcp as tcp
import command_udp as udp

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

def handle_udp(sock):
    pass

def main():
    if len(sys.argv) != 4:
        print(f'usage: {sys.argv[0]} <tcp|udp> <address> <port>')
        return

    protocol = sys.argv[1]
    address = sys.argv[2]
    port = int(sys.argv[3])

    socket.setdefaulttimeout(30)

    if protocol == 'tcp':
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    elif protocol == 'udp':
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        print(f'error: unknown protocol \'{protocol}\'')
        return

    try:
        sock.connect((address, port))
    except TimeoutError:
        print('error: timed out'); sock.close()
        return

    if protocol == 'tcp':
        handle_tcp(sock)
    else:
        handle_udp(sock)

    sock.close()

if __name__ == "__main__":
    main()
