import socket

class Srv:
    def __init__(self, name):
        self.name = name
        self._running = False

    def start(self):
        if not self._running:
            print(f"Starting {self.name} service...")
            self._running = True
            # tcpサーバを起動する
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('localhost', 0))
            self.server_socket.listen(1)
            self.port = self.server_socket.getsockname()[1]
            print(f"{self.name} service started on port {self.port}")
            # サーバが起動したことを確認する
            conn, addr = self.server_socket.accept()
            print(f"Connection from {addr} has been established.")
            conn.close()
        else:
            print(f"{self.name} service is already running.")

    def stop(self):
        if self._running:
            print(f"Stopping {self.name} service...")
            self._running = False
        else:
            print(f"{self.name} service is not running.")
