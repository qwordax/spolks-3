import logging
import socket
import sys

import command_tcp as tcp
import command_udp as udp

def handle_tcp(sock):
    sock.listen(1)

    working = True
    timeout = 0

    while working and timeout < 3:
        logging.info('accepting . . .')

        try:
            conn, address = sock.accept()
            logging.info(f'accepted {address[0] + ":" + str(address[1])}')
        except TimeoutError:
            logging.info('timeout'); timeout += 1
            continue

        try:
            while True:
                args = conn.recv(tcp.BUFSIZE).decode('ascii').split()

                if args[0] == 'close':
                    working = False
                    break

                if args[0] == 'exit' or args[0] == 'quit':
                    break

                logging.info(' '.join(args))

                if args[0] == 'echo':
                    tcp.server_echo(conn, args)
                elif args[0] == 'time':
                    tcp.server_time(conn)
                elif args[0] == 'upload':
                    tcp.server_upload(conn, address)
                elif args[0] == 'download':
                    tcp.server_download(conn, address, args)
                else:
                    tcp.server_unknown(conn, args)
        except ConnectionAbortedError:
            tcp.FATAL = True

            logging.critical(
                f'connection aborted {address[0]+":"+str(address[1])}')
        except ConnectionResetError:
            tcp.FATAL = True

            logging.critical(
                f'connection reset {address[0]+":"+str(address[1])}')
        except TimeoutError:
            tcp.FATAL = True

            logging.critical(
                f'timeout {address[0]+":"+str(address[1])}')
        finally:
            logging.info(
                f'closed {address[0]+":"+str(address[1])}')

            conn.close()

def handle_udp(sock):
    pass

def main():
    if len(sys.argv) != 4:
        print(f'usage: {sys.argv[0]} <tcp|udp> <address> <port>')
        return

    protocol = sys.argv[1]
    address = sys.argv[2]
    port = int(sys.argv[3])

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s : %(message)s'
        )

    socket.setdefaulttimeout(30)

    if protocol == 'tcp':
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    elif protocol == 'udp':
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        print(f'error: unknown protocol \'{protocol}\'')
        return

    sock.bind((address, port))

    if protocol == 'tcp':
        handle_tcp(sock)
    else:
        handle_udp(sock)

    logging.info('closing . . .')
    sock.close()

if __name__ == "__main__":
    main()
