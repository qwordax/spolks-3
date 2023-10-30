import logging
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

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s : %(message)s'
        )

    socket.setdefaulttimeout(30)

    if protocol == 'tcp':
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        command_echo = command_tcp.server_echo
        command_time = command_tcp.server_time
        command_upload = command_tcp.server_upload
        command_download = command_tcp.server_download
        command_unknown = command_tcp.server_unknown
    elif protocol == 'udp':
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        command_echo = command_udp.server_echo
        command_time = command_udp.server_time
        command_upload = command_udp.server_upload
        command_download = command_udp.server_download
        command_unknown = command_udp.server_unknown
    else:
        print(f'error: unknown protocol \'{protocol}\'')
        return

    sock.bind((address, port))

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
                args = conn.recv(command_tcp.BUFSIZE).decode('ascii').split()

                if args[0] == 'close':
                    working = False
                    break

                if args[0] == 'exit' or args[0] == 'quit':
                    break

                logging.info(' '.join(args))

                if args[0] == 'echo':
                    command_echo(conn, args)
                elif args[0] == 'time':
                    command_time(conn)
                elif args[0] == 'upload':
                    command_upload(conn, address)
                elif args[0] == 'download':
                    command_download(conn, address, args)
                else:
                    command_unknown(conn, args)
        except ConnectionAbortedError:
            command_tcp.FATAL = True

            logging.critical(
                f'connection aborted {address[0]+":"+str(address[1])}')
        except ConnectionResetError:
            command_tcp.FATAL = True

            logging.critical(
                f'connection reset {address[0]+":"+str(address[1])}')
        except TimeoutError:
            command_tcp.FATAL = True

            logging.critical(
                f'timeout {address[0]+":"+str(address[1])}')
        finally:
            logging.info(
                f'closed {address[0]+":"+str(address[1])}')

            conn.close()

    logging.info('closing . . .')
    sock.close()

if __name__ == "__main__":
    main()
