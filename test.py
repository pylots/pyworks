from socket import socket, AF_INET, SOCK_STREAM
from select import select

serversocket = socket(AF_INET, SOCK_STREAM)
serversocket.bind(('localhost', 8080))
print("bound")
serversocket.listen(2)
print("listened")
host, port = serversocket.getsockname()
print("accepting on %s:%d" % (host, port))
sock, address = serversocket.accept()

print("accepted: %s:%s" % (sock, address))

while True:
    inputs = [sock]
    # self.sock.setblocking(0) # Jython compatibility
    inp, outp, x = select(inputs, [], [], 0.1)
    print(">>%s" % sock.recv(4096))
