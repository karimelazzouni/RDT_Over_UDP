import packet_gen as pac_gen
import socket
import pickle as pick
import threading

class StopAndWait : 

    BUF_SIZE = 4096 # max size of received packet (ACK)

    def __init__(self,file_name, t_sock, rec_addr, time_out) :
        self.socket         = t_sock
        self.dest           = rec_addr
        self.time_out       = time_out
        self.time_out_sock  = time_out*10 # Socket timeout is 10 times the packet timeout
        self.gen            = pac_gen.PacketGen(file_name)
        self.socket.settimeout(self.time_out_sock)

    def send(self):
        packet = (self.gen).gen_packet_from_file()
        while packet:
            print ("Sending: packet ", packet.seqno)
            (self.socket).sendto(pick.dumps(packet), self.dest)
            timer = threading.Timer(self.time_out,timer_handler,args=(self, packet,))
            timer.start()
            
            # wait for ACK or abort after a long period of time
            while 1 :
                ack = None
                addr = None
                try :
                    print ("\tWaiting For ACK: packet ", packet.seqno)
                    ack, addr = (self.socket).recvfrom(self.BUF_SIZE)
                except self.socket.timeout :
                    print ("Error: 10 retransmissions of packet have occured yet no ACKs were received. Aborting.")
                    timer.cancel()
                    return None

                if addr == self.dest and pick.loads(ack).ackno == packet.seqno : # correct ACK received
                    print ("\tACK received for packet ", packet.seqno)
                    timer.cancel()
                    packet = self.gen.gen_packet_from_file() # update the packet
                    break
                else :
                    print("\tWrong ACK or Wrong sender")
        print ("File has been transferred successfully.")

def timer_handler(self, packet):
    # retransmit packet to the same client
    print ("\tTimeout: retransmitting packet ", packet.seqno)
    (self.socket).sendto(pick.dumps(packet), self.dest)
