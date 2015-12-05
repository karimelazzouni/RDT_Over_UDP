import packet_gen as pac_gen
import socket
import pickle as pick
import threading
import pac_ack_t as packt

class SelectiveRepeat:
    def __init__(self, file_name, t_sock, rec_addr, time_out, window_size):
        self.socket    = t_sock
        self.dest      = rec_addr
        self.time_out  = time_out
        self.gen       = pac_gen.PacketGen(file_name)
        self.list_size = window_size 
        self.socket.settimeout(self.time_out_sock)
        
        self.lock  = threading.Lock()
        self.packt = packt.PackACKTime()
        self.base_seqno  = -1
        self.init_selective_repeat()

    def init_selective_repeat(self):
        i = 0
        while i < self.list_size:
            self.packt.packet_list.append((self.gen).gen_packet_from_file())
            self.packt.ack_list.append(0)
            self.packt.timer_list.append(None)
            i++
        self.base_seqno = self.packet_list[0].seqno

    def send_packet(self, packet):
        self.lock.acquire()
        index = packet.seqno - self.base_seqno
        if index >= 0:
            self.socket.sendto(pick.dumps(packet), self.rec_addr)
            self.packt.timer_list[packet.seqno - self.base_seqno] = threading.Timer(self.time_out,self.timer_handler,args=(packet,))
            self.packt.timer_list[packet.seqno - self.base_seqno].start()
        self.lock.release()

    def wait_for_ack(self,packet):
        # wait for ACK or abort after a long period of time
        while 1 :
            ack = None
            addr = None
            try :
                ack, addr = (self.socket).recvfrom(self.BUF_SIZE)
            except self.socket.timeout :
                print ("Error: 10 retransmissions of packet have occured yet no ACKs were received. Aborting.")
                return None

            if addr == self.dest: # correct ACK received
                ackno =  pick.loads(ack).ackno
                print ("\tACK received for packet ", ackno)
                self.check_list(ackno)
                if len(self.packt.ack_list) == 0:
                    break
            else :
                print("\tWrong sender")

    def send_all_packets(self):
        i = 0
        while i < self.list_size:
            send_packet(self.packt.packet_list[i])
            i++

    def check_list(self, ackno):
        self.lock.acquire()
        index = ackno - self.base_seqno
        if index >=0 :
            self.packt.timer_list[ackno - base_seqno].cancel()
            self.packt.ack_list[ackno - base_seqno] = 1
            if self.packt.ack_list[0] == 1:
                while self.packt.ack_list[0] == 1:
                    self.packt.packet_list.pop(0)
                    self.packt.ack_list.pop(0)
                    self.packt.timer_list.pop(0)

                    packet = self.gen.gen_packet_from_file()
                    if packet:
                        self.packt.packet_list.append(packet)
                        self.packt.ack_list.append(0)
                        self.packt.timer_list.append(None)
                        self.socket.sendto(pick.dumps(packet), self.rec_addr)
                        self.packt.timer_list[packet.seqno - self.base_seqno] = threading.Timer(self.time_out,timer_handler,args=(self, packet,))
                        self.packt.timer_list[packet.seqno - self.base_seqno].start()

                    self.base_seqno = self.packt.packet_list[0].seqno
        self.lock.release()

    def send_file(self):
        sending_all_thread  = threading.Thread(target = self.send_all_packets, args=( ))
        wait_for_ack_thread = threading.Thread(target = self.wait_for_ack, args=( ))
        sending_all_thread.setName("Send All packets.")
        wait_for_ack_thread.setName("Wait for ACK.")
        sending_all_thread.start()
        wait_for_ack_thread.start()

    def timer_handler(self, packet):
        self.lock.acquire()

        # self.packt.timer_list[packet.seqno - self.base_seqno].cancel()
        index = packet.seqno - self.base_seqno
        if index >= 0:
            self.socket.sendto(pick.dumps(packet), self.dest)
            self.packt.timer_list[packet.seqno - self.base_seqno] = threading.Timer(self.time_out, self.timer_handler, args=(packet, ))
            self.packt.timer_list[packet.seqno - self.base_seqno].start()

        self.lock.release()