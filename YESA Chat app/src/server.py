import threading
import socket
import argparse
import os
import sys


class Server(threading.Thread):

    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))

        sock.listen(1)
        print(f"Listening at {sock.getsockname()}")

        while True:
            sc, sockname = sock.accept()
            print(f"Accepting a new connection from {sc.getpeername()} to {sc.getsockname()}")

            # Create a new thread
            server_socket = ServerSocket(sc, sockname, self)
            server_socket.start()

            self.connections.append(server_socket)
            print("Ready to receive messages from", sc.getpeername())

    def broadcast(self, message, source):
        for connection in self.connections:
            if connection.sockname != source:
                connection.send(message)

    def remove_connection(self, connection):
        self.connections.remove(connection)


class ServerSocket(threading.Thread):

    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server

    def run(self):
        while True:
            message = self.sc.recv(1024).decode('ascii')

            if message:
                print(f"{self.sockname} says {message}")
                self.server.broadcast(message, self.sockname)
            else:
                print(f"{self.sockname} has closed the connection")
                self.server.remove_connection(self)
                self.sc.close()
                break

    def send(self, message):
        self.sc.sendall(message.encode('ascii'))

def shutdown_server(server):
    ipt = input("")
    if ipt == "q":
        print("Closing all connections...")
        for connection in server.connections:
            connection.sc.close()

        print("Shutting down the server...")
        sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chatroom Server")
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060, help='TCP port (default 1060)')

    args = parser.parse_args()

    server = Server(args.host, args.p)
    server.start()

    exit_thread = threading.Thread(target=shutdown_server, args=(server,))
    exit_thread.start()
