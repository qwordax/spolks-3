import socket
import sys

import command_tcp
import command_udp

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

        command_echo = command_tcp.client_echo
        command_time = command_tcp.client_time
        command_upload = command_tcp.client_upload
        command_download = command_tcp.client_download
        command_unknown = command_tcp.client_unknown
    elif protocol == 'udp':
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        command_echo = command_udp.client_echo
        command_time = command_udp.client_time
        command_upload = command_udp.client_upload
        command_download = command_udp.client_download
        command_unknown = command_udp.client_unknown
    else:
        print(f'error: unknown protocol \'{protocol}\'')
        return

    try:
        sock.connect((address, port))
    except TimeoutError:
        print('error: timed out'); sock.close()
        return

    while True:
        args = input('> ').split()

        if args == []:
            continue

        try:
            if args[0] == 'close' or args[0] == 'exit' or args[0] == 'quit':
                sock.send(' '.join(args).encode('ascii'))
                break

            if args[0] == 'echo':
                command_echo(sock, args)
            elif args[0] == 'time':
                command_time(sock, args)
            elif args[0] == 'upload':
                command_upload(sock, args)
            elif args[0] == 'download':
                command_download(sock, args)
            else:
                command_unknown(sock, args)
        except ConnectionAbortedError:
            print('error: connection aborted')
            break
        except ConnectionResetError:
            print('error: connection reset')
            break
        except TimeoutError:
            print('error: timeout')
            break

    sock.close()

if __name__ == "__main__":
    main()
