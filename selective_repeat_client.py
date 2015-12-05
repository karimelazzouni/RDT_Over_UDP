import packet_gen as pac_gen
import socket
import pickle as pick
import threading
import ack
import os

class SelectiveRepeat:
    BUF_SIZE = 4096 # max size of received packet.
    def __init__(self, file_name, sock, server_addr, time_out, window_size):
        self.socket        = sock
        self.dest          = server_addr
        self.time_out      = time_out
        self.sock_time_out = time_out*10
        self.list_size     = window_size
        self.file          = open(file_name, 'ab')
        self.socket.settimeout(self.sock_time_out)

        self.buffer     = []
        self.base_seqno = 1 #Assuming the first seqno = 1
        self.init_lists()

    def init_lists(self) :
        for i in range(0, self.list_size):
            self.buffer.append(None)

    def recv_one_packet(self) :
        byte, addr = (self.socket).recvfrom(self.BUF_SIZE)

        packet = pick.loads(byte)

        if addr == self.dest :
            self.check_packet(packet)
            print("Received packet ", packet.seqno)
            if packet.seqno == 0 :
                return 0
            return 1
        
    def check_packet(self, packet) :
        index = packet.seqno - self.base_seqno
        if index < 0 : #Already written packet
            ack_packet = ack.Ack(0, packet.seqno)
            self.socket.sendto(pick.dumps(ack_packet), self.dest)
        
        if index >= 0 and index < self.list_size : #packet in range
            if not self.buffer[index] : #packet received for the first time
                self.buffer[index] = packet
                ack_packet = ack.Ack(0, packet.seqno)
                self.socket.sendto(pick.dumps(ack_packet), self.dest)
            else : #packet was received before
                ack_packet = ack.Ack(0, packet.seqno)
                self.socket.sendto(pick.dumps(ack_packet), self.dest)

        self.check_buffer()

    def check_buffer(self) :
        if self.buffer[0] : #start updating window
            while self.buffer[0] :
                packet = self.buffer[0]
                for i in range(len(packet.data)) :
                    self.file.write(packet.data[i])
                self.file.flush()
                self.buffer.pop(0)
                self.buffer.append(None)
                self.base_seqno = self.base_seqno + 1
    
    def recv_file(self) :
        while 1:
            try:
                in_progress = self.recv_one_packet()
                if not in_progress:
                    print("File Received Successfully.")
                    self.file.close()
                    break
            except self.socket.timeout:
                self.file.close()
                break