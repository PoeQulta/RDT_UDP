from RDT_Sock import RDT_Socket
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
