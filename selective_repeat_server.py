import packet_gen as pac_gen
import socket
import pickle as pick
import threading
import pac_ack_t as packt
import PLS

class SelectiveRepeat:
    BUF_SIZE = 4096
    def __init__(self, file_name, t_sock, rec_addr, time_out, p_loss, window_size):
        self.socket        = t_sock
        self.dest          = rec_addr
        self.time_out      = time_out
        self.time_out_sock = time_out*10
        self.gen           = pac_gen.PacketGen(file_name)
        self.p_loss 	   = p_loss
        self.list_size     = window_size 
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
            i = i + 1
        self.base_seqno = self.packt.packet_list[0].seqno

    def send_packet(self, packet):
        index = packet.seqno - self.base_seqno
        if index >= 0:
            print("Sending: packet ", packet.seqno)
            if not PLS.lose_packet(self.p_loss) :
            	self.socket.sendto(pick.dumps(packet), self.dest)
            self.packt.timer_list[packet.seqno - self.base_seqno] = threading.Timer(self.time_out,self.timer_handler,args=(packet,))
            self.packt.timer_list[packet.seqno - self.base_seqno].start()

    def wait_for_ack(self):
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
                    end = (self.gen).gen_close_packet()
                    if not PLS.lose_packet(self.p_loss) :
                    	(self.socket).sendto(pick.dumps(end), self.dest)
                    break
            else :
                print("\tWrong sender")

    def send_all_packets(self):
        curr_seqno = 1
        while curr_seqno <= self.list_size:
            self.lock.acquire()
            expected_index = curr_seqno - self.base_seqno
            self.send_packet(self.packt.packet_list[expected_index])
            curr_seqno = curr_seqno + 1
            self.lock.release()

    def check_list(self, ackno):
        self.lock.acquire()
        index = ackno - self.base_seqno
        if index >=0 :
            self.packt.timer_list[ackno - self.base_seqno].cancel()
            self.packt.ack_list[ackno - self.base_seqno] = 1
            if self.packt.ack_list[0] == 1:
                while self.packt.ack_list[0] == 1:
                    self.packt.packet_list.pop(0)
                    self.packt.ack_list.pop(0)
                    self.packt.timer_list.pop(0)

                    packet = self.gen.gen_packet_from_file()
                    if len(self.packt.packet_list) > 0:
                        self.base_seqno = self.packt.packet_list[0].seqno
                    else:
                        # print("WE ARE HERE")
                        break
                    if packet:
                        self.packt.packet_list.append(packet)
                        self.packt.ack_list.append(0)
                        self.packt.timer_list.append(None)
                        if not PLS.lose_packet(self.p_loss) :
                        	self.socket.sendto(pick.dumps(packet), self.dest)
                        self.packt.timer_list[packet.seqno - self.base_seqno] = threading.Timer(self.time_out,self.timer_handler,args=(packet,))
                        self.packt.timer_list[packet.seqno - self.base_seqno].start()

        self.lock.release()

    def send_file(self):
        sending_all_thread  = threading.Thread(target = self.send_all_packets, args=( ))
        wait_for_ack_thread = threading.Thread(target = self.wait_for_ack, args=( ))
        sending_all_thread.setName("Send All packets.")
        wait_for_ack_thread.setName("Wait for ACK.")
        sending_all_thread.start()
        wait_for_ack_thread.start()

        sending_all_thread.join()
        wait_for_ack_thread.join()

    def timer_handler(self, packet):
        self.lock.acquire()
        print ("\tTimeout: retransmitting packet ", packet.seqno)
        # self.packt.timer_list[packet.seqno - self.base_seqno].cancel()
        index = packet.seqno - self.base_seqno
        if index >= 0:
            if not PLS.lose_packet(self.p_loss) :
            	self.socket.sendto(pick.dumps(packet), self.dest)
            self.packt.timer_list[packet.seqno - self.base_seqno] = threading.Timer(self.time_out, self.timer_handler, args=(packet, ))
            self.packt.timer_list[packet.seqno - self.base_seqno].start()

        self.lock.release()