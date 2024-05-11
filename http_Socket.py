from RDT_Sock import RDT_Socket
class HTTPRequestHandler:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port

    def start(self):
        server_socket = RDT_Socket()
        server_socket.bind((self.host,self.port))
        server_socket.listen(1)
        print(f"Server started at {self.host}:{self.port}")
        conn = server_socket.accept()
        print(f'Connected by {conn.remote_IP}:{conn.remote_port}' )
        while True:
                try:
                    data = conn.receive()
                    if not data:
                        break
                    request = data.decode('utf-8')
                    print('Request:', request)
                    response = self.handle_request(request)
                    conn.send(response.encode('utf-8'))
                except ConnectionAbortedError:
                    print(f'Connection Aborted by {conn.remote_IP}:{conn.remote_port}' )
                    conn = server_socket.accept()

    def parse_headers(self, request):
        headers = request.split('\n')
        first_line = headers[0].split()
        method = first_line[0]
        url = first_line[1]

        headers_dict = {}
        for header in headers[1:]:
            if header:
                key, value = header.split(': ')
                headers_dict[key] = value

        return method, url, headers_dict
    
    def handle_request(self, request):
        headers = request.split('\r\n')
        first_line = headers[0].split()
        method = first_line[0]
        url = first_line[1]

        if method == 'GET':
            return self.handle_get(url,headers)
        if method == 'POST':
            return self.handle_post(url,headers)
        else:
            return 'HTTP/1.0 405 Method Not Allowed\r\n'
    def handle_post(self, url, headers):
        response_headers = {
            'Content-Type': 'text/html',
        }

        if url == '/':
            response_body = 'Form submitted!'
            response_headers['Content-Length'] = len(response_body)
            response = 'HTTP/1.0 200 OK\r\n'
        else:
            response_body = ''
            response_headers['Content-Length'] = 0
            response = 'HTTP/1.0 404 Not Found\r\n'

        for key, value in response_headers.items():
            response += f'{key}: {value}\r\n'
        response += '\r\n'
        response += response_body

        return response

    def handle_get(self, url, headers):
        response_headers = {
            'Content-Type': 'text/html',
        }

        if url == '/':
            response_body = 'Hello, World!'
            response_headers['Content-Length'] = len(response_body)
            response = 'HTTP/1.0 200 OK\r\n'
        else:
            response_body = ''
            response_headers['Content-Length'] = 0
            response = 'HTTP/1.0 404 Not Foundr\r\n'

        for key, value in response_headers.items():
            response += f'{key}: {value}\r\n'
        response += '\r\n'
        response += response_body

        return response

class HTTPClient:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
    def connect(self):
        self.client_socket = RDT_Socket(timeout=5)
        self.conn = self.client_socket.handshake((self.host, self.port))
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.client_socket = None
        
    def send_request(self, method, url, headers=None, body=None):
        if not self.client_socket:
            self.connect()

        request_line = f"{method} {url} HTTP/1.0\r\n"
        headers = headers or {}
        headers['Host'] = self.host
        headers_str = ''.join(f'{k}: {v}\r\n' for k, v in headers.items())
        body = body or ''
        request = f"{request_line}{headers_str}\r\n{body}"
        self.conn.send(request.encode('utf-8'))     
        response = self.conn.receive().decode('utf-8')
        return self.parse_response(response)

    def parse_response(self, response):
        status_line, headers = response.split('\r\n', 1)
        headers_str, body = headers.split('\r\n\r\n', 1)
        version, status, reason = status_line.split(' ', 2)
        headers = self.parse_headers(headers_str)

        return {
            'version': version,
            'status': status,
            'reason': reason,
            'headers': headers,
            'body': body,
        }

    def parse_headers(self, headers_str):
        headers = {}
        for line in headers_str.split('\r\n'):
            key, value = line.split(': ', 1)
            headers[key] = value
        return headers
