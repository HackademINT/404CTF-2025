import socket
import threading
import re

from request import Request
from response import Response

class Route:
    def __init__(self, path_regex, handler):
        self.path_regex = path_regex
        self.handler = handler

    def match(self, path):
        match = re.match(self.path_regex, path)
        return True if match else False

class HTTPServer:
    def __init__(self, host, port, fallback_route_handler):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.routes = []
        self.fallback_route_handler = fallback_route_handler

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server running on http://{self.host}:{self.port}/")

        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()
        finally:
            self.server_socket.close()

    def handle_client(self, client_socket, addr):
        try:
            buffer = ''
            while True:
                chunk = client_socket.recv(1024).decode('utf-8')
                if not chunk:
                    break
                buffer += chunk
                if '\r\n\r\n' in buffer:
                    break
            request = Request(buffer)

            if request.method != 'GET':
                response = Response(405, 'Method Not Allowed')
            else:
                route = next((r for r in self.routes if r.match(request.path)), None)
                if route:
                    response = route.handler(request)
                else:
                    response = self.fallback_route_handler(request)

            response_data = response.build()
            client_socket.sendall(response_data.encode('utf-8'))
        except Exception as e:
            error_response = Response(500, f"<h1>500 Internal Server Error</h1><p>{e}</p>")
            client_socket.sendall(error_response.build().encode('utf-8'))
        finally:
            client_socket.close()