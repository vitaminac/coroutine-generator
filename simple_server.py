# coding=utf-8
from systemcall import ReadWait, WriteWait, NewTask
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from scheduler import Scheduler


class Socket(object):
    def __init__(self, sock):
        self.sock = sock

    def accept(self):
        yield from ReadWait(self.sock)
        client, addr = self.sock.accept()
        return Socket(client), addr

    def send(self, buffer):
        while buffer:
            yield from WriteWait(self.sock)
            len = self.sock.send(buffer)
            print("sent:", buffer)
            buffer = buffer[len:]

    def recv(self, maxbytes):
        yield from ReadWait(self.sock)
        data = self.sock.recv(maxbytes)
        print("recv", data)
        return data

    def close(self):
        yield self.sock.close()


def handle_client(client, addr):
    print("Connection from", addr)
    while True:
        data = yield from client.recv(65536)
        if not data:
            break
        yield from client.send(data)
    print("Client closed")
    yield from client.close()


def server(port = 48539):
    print("Server starting")
    rawsock = socket(AF_INET, SOCK_STREAM)
    rawsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    rawsock.bind(("0.0.0.0", port))
    rawsock.listen(1024)

    sock = Socket(rawsock)
    while True:
        client, addr = yield from sock.accept()
        yield from NewTask(handle_client(client, addr))


if __name__ == '__main__':
    scheduler = Scheduler()
    scheduler.create_task(server())
    scheduler.run_forever()
