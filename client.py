import socket
import packet as pac
import packet_gen as pac_gen
import pickle as pick
import stop_wait_client as swc

SERVER_IP = "127.0.0.1"
SERVER_PORT = 55555
CLIENT_IP = "127.0.0.1"
CLIENT_PORT = 44444

# print ("UDP target IP:", UDP_IP)
# print ("UDP target port:", UDP_PORT)
# print ("message:", MESSAGE)
 
sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP
sock.bind((CLIENT_IP,CLIENT_PORT))

gen = pac_gen.PacketGen()
packet = gen.gen_packet("/tmp/server/text.txt")
pac_bytes = pick.dumps(packet)

sock.sendto(pac_bytes, (SERVER_IP, SERVER_PORT))
data, addr = sock.recvfrom(1024)
#if timeout close the connection
# print ("Received: ", data.decode('UTF-8'), "from ",addr)
# print ("Server addr: ",addr)
# print ("Client addr: ",sock)
sw = swc.StopAndWait("/tmp/client/text.txt",sock, addr, 10)
sw.recv_file()