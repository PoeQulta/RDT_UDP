from packet import Packet
import socket
import struct
class RDT_Socket(socket.socket):
    class connection():
        def __init__(self,sock,remote_addrs) -> None:
            try:
                self.local_ip,self.local_port = sock.getsockname()
            except OSError:
                sock.bind(('localhost',0))
                self.local_ip,self.local_port = sock.getsockname()
            self.remote_IP =socket.gethostbyname(remote_addrs[0]) 
            self.remote_port = remote_addrs[1]
            self.seq_num = 0
            self.ack_num = 0
            self.window_size = 1
            self.sock = sock
        def send(self, data):
            size = struct.calcsize(Packet.packet_format)
            packet = Packet(self.seq_num, self.ack_num, data, self.window_size)
            self.sock.sendto(packet.get_packed(),(self.remote_IP,self.remote_port))
            try:
                ackData, addr = self.sock.recvfrom(2048)
                ackPacket = Packet.from_struct(ackData)
                if(addr[0]==self.remote_IP and addr[1]==self.remote_port):
                    if(ackPacket.flags.ACK):
                        if(ackPacket.ack_num == packet.seq_num+size):
                            print("Recieved ACK")
                            self.seq_num = ackPacket.ack_num
                            self.ack_num = ackPacket.seq_num+1
                            return True
            except TimeoutError:
                print("Resending Data")
                self.send(data)
            raise Exception("send Failure")
        def acknowledge(self,packet:Packet):
            size = struct.calcsize(Packet.packet_format)
            self.ack_num = packet.seq_num + size
            self.seq_num = packet.ack_num
            ack_packet = Packet(self.seq_num, self.ack_num, b'', self.window_size, ACK=True)
            self.sock.sendto(ack_packet.get_packed(), (self.remote_IP,self.remote_port))

        def receive(self):
            data, addr = self.sock.recvfrom(2048)
            if(addr[0]==self.remote_IP and addr[1]==self.remote_port):
                packet = Packet.from_struct(data)
                if packet.flags.FIN:
                    Fin_ack_packet = Packet(self.seq_num, self.ack_num, b'', self.window_size, ACK=True,FIN=True)
                    self.sock.sendto(Fin_ack_packet.get_packed(), (self.remote_IP,self.remote_port))
                    raise ConnectionAbortedError
                if packet.checksum == packet.crc_32_func(packet.data):
                    self.acknowledge(packet)
                    return packet.data.strip(b'\0')
                else:
                    raise Exception("Checksum error")
        def close(self):
            Fin_packet = Packet(self.seq_num, self.ack_num, b'', self.window_size,FIN=True)
            self.sock.sendto(Fin_packet.get_packed(), (self.remote_IP,self.remote_port))
            try:
                resp = self.receive()
                return False
            except ConnectionAbortedError:
                self.sock.close()
                return True


    def __init__(self,timeout=None) -> None:
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        super().settimeout(timeout)
    def listen(self, backlog):
        self.backlog = backlog
        self.connections = []
    def handshake(self, addr):
        conn = self.connection(self,addr)
        # Send SYN packet
        print("Initiating Handshake")
        syn_packet = Packet(conn.seq_num, conn.ack_num, b'', conn.window_size, SYN=True)
        super().sendto(syn_packet.get_packed(), addr)
        # Receive SYN-ACK packet
        data, _ = super().recvfrom(2048)
        syn_ack_packet = Packet.from_struct(data)
        if syn_ack_packet.flags.SYN and syn_ack_packet.flags.ACK:
            print("Recieved SYN_ACK")
            conn.ack_num = syn_ack_packet.seq_num + 1
        # Send ACK packet
        print("Sending ACK")
        ack_packet = Packet(conn.seq_num, conn.ack_num, b'', conn.window_size, ACK=True)
        super().sendto(ack_packet.get_packed(), addr)
        return conn
    def accept(self):
        while True:
            data, addr = super().recvfrom(2048)
            packet = Packet.from_struct(data)
            if packet.flags.SYN:
                print("Accepting Handshake")
                return self.handle_connection(packet,addr)
    def handle_connection(self, packet,addr):
        conn = self.connection(self,addr)
        conn.ack_num = packet.seq_num +1
        syn_ack_packet = Packet(conn.seq_num, conn.ack_num, b'', conn.window_size, SYN=True,ACK=True)
        print("Sending SYN_ACK")
        super().sendto(syn_ack_packet.get_packed(), addr)
         # Receive ACK packet
        data, _ = super().recvfrom(2048)
        ack_packet = Packet.from_struct(data)
        if syn_ack_packet.flags.ACK:
            if ack_packet.ack_num == syn_ack_packet.seq_num+1:
                print("Recieved ACK")
                return conn
        raise Exception("Handshake Ack Failed")
    def close(self):
        super().close()