import packet_gen as pac_gen
import socket
import pickle as pick
import threading
import ack
import os

class StopAndWait : 

    BUF_SIZE = 4096 # max size of received packet.

    def __init__(self, file_name, sock, server_addr, time_out) :
        self.socket         = sock
        self.dest           = server_addr
        self.time_out       = time_out
        self.time_out_sock  = time_out*10 # Socket timeout is 10 times the packet timeout
        self.file           = open(file_name, 'ab')
        self.socket.settimeout(self.time_out_sock)

    def recv_one_packet(self):
        byte,addr = self.socket.recvfrom(self.BUF_SIZE)
        packet = pick.loads(byte)


        print("Received packet ", packet.seqno)
        
        for i in range(len(packet.data)) :
            self.file.write(packet.data[i])
        
        self.file.flush()
        # os.fsync()
        ack_packet = ack.Ack(0, packet.seqno)
        # self.socket.sendto(pick.dumps(ack_packet), self.dest)

    def recv_file(self):
        while 1:
            try:
                self.recv_one_packet()
            except self.socket.timeout:
                print("File Received Successfully.")
                self.file.close()
                break
