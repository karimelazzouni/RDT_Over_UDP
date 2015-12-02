import socket
import packet as pac
import packet_gen as pac_gen
import pickle

UDP_IP = "127.0.0.1"
UDP_PORT = 55555
MESSAGE = "Hello, World!"
 
print ("UDP target IP:", UDP_IP)
print ("UDP target port:", UDP_PORT)
print ("message:", MESSAGE)
 
sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP

gen = pac_gen.PacketGen()
packet = gen.gen_packet("ABCD.txt")
pac_bytes = pickle.dumps(packet)

sock.sendto(pac_bytes, (UDP_IP, UDP_PORT))
data, addr = sock.recvfrom(1024)
print ("Received: ", data.decode('UTF-8'), "from ",addr)