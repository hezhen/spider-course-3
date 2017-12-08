import socket

class SocketClient:
    def __init__(self, server_ip='localhost', server_port=20010):
        self.server_ip = server_ip
        self.server_port = server_port

    def send(self, message):
        try:
            # Create a TCP/IP socket
            self.sock = socket.create_connection((self.server_ip, self.server_port))
            # Send data
            self.sock.sendall(message)

            data = self.sock.recv(1024)

            return data
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            if msg[0] is 61:
                return None
        finally:
            if hasattr(self, 'sock'):
                self.sock.close()