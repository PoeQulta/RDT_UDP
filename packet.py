import struct
from crcmod import mkCrcFun

class Packet():

    class Flags():
        def __init__(self,SYN,ACK,FIN,RST) -> None:
            self.SYN = SYN
            self.ACK = ACK
            self.FIN = FIN
            self.RST = RST

    #packet format = Seq_num(int),Ack_num(int),SYN(bool),ACK(bool),FIN(bool),RST(bool),Window_size(int),Checksum(int),data(1024 bytes)
    packet_format = '!I I ? ? ? ? I I 1024s'
    @classmethod
    def from_struct(cls, packet):
        seq_num, ack_num, syn, ack, fin, rst, window_size, checksum, data = struct.unpack(cls.packet_format, packet)
    
        return cls(seq_num, ack_num, data, window_size, syn, ack, fin, rst,checksum)
    def __init__(self,seq_num,ack_num,data,window_size=1,SYN=False,ACK=False,FIN=False,RST=False,checksum=None) -> None:
        self.crc_32_func = mkCrcFun(0x104c11db7, initCrc=0, xorOut=0xFFFFFFFF)
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.flags = self.Flags(SYN,ACK,FIN,RST)
        self.window_size = window_size
        self.data =self.pad_data(data)
        if checksum:
            self.checksum = checksum
        else:
        # Ensure the data is in bytes format
            if isinstance(data, str):
                data = data.encode()
            self.checksum = self.crc_32_func(self.data)
    def pad_data(self, data):
        # Ensure the data is always 1024 bytes
        #return data
        return data.ljust(1024, b'\0')
    def get_packed(self):
        return struct.pack(self.packet_format,
                            self.seq_num,
                            self.ack_num,
                            self.flags.SYN,
                            self.flags.ACK,
                            self.flags.FIN,
                            self.flags.RST,
                            self.window_size,
                            self.checksum,
                            self.data)
    
