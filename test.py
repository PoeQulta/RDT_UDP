from RDT_Sock import RDT_Socket
from http_Socket import HTTPRequestHandler,HTTPClient
# Server Code
def server():
    server_socket = RDT_Socket()
    server_socket.bind(('localhost', 12345))
    server_socket.listen(1)
    print("Server is listening...")
    while True:
        conn = server_socket.accept()
        print("Connection established.")
        data = conn.receive()
        print("Received data:", data.decode())
        conn.send(b"Hello from server!")
        print("Sent acknowledgment.")

# Client Code
def client():
    client_socket = RDT_Socket()
    conn = client_socket.handshake(('localhost', 12345))
    print("Connection established.")
    conn.send(b"Hello from client!")
    print("Sent data.")
    data = conn.receive()
    print("Received acknowledgment:", data.decode())
    conn.close()
    client_socket.close()


def HTTPServerTest():
    server = HTTPRequestHandler()
    server.start()
def HTTPClientTest():
    client = HTTPClient()
    client.connect()
    # Send a GET request
    response = client.send_request('GET', '/')
    # Print the response
    print(response) 
    # Send a POST request
    response = client.send_request('POST', '/')
    # Print the response
    print(response)
    client.close()
