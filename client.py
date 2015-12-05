import socket
import packet as pac
import packet_gen as pac_gen
import pickle as pick
import stop_wait_client as swc
import selective_repeat_client as sr

CLIENT_IP = "127.0.0.1"
BUF_SIZE = 4096

def read_in(file_name) :
	with open(file_name) as f :
		SERVER_IP = f.readline()
		SERVER_PORT = int(f.readline())
		CLIENT_PORT = int(f.readline())
		FILE_NAME = f.readline()
		FILE_NAME = FILE_NAME.rstrip('\n')
		REC_WINDOW = int(f.readline())
		TIMEOUT = int(f.readline())
	return (SERVER_IP,SERVER_PORT,CLIENT_PORT,FILE_NAME,REC_WINDOW, TIMEOUT)

(SERVER_IP,SERVER_PORT,CLIENT_PORT,FILE_NAME,REC_WINDOW,TIMEOUT) = read_in("/tmp/client/client.in")
FILE_NAME_ARR = FILE_NAME.split("/")
FILE_DEST = "/tmp/client/" + FILE_NAME_ARR[len(FILE_NAME_ARR)-1]
sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP
sock.bind((CLIENT_IP,CLIENT_PORT))

gen = pac_gen.PacketGen()
packet = gen.gen_packet(FILE_NAME)
pac_bytes = pick.dumps(packet)

sock.sendto(pac_bytes, (SERVER_IP, SERVER_PORT))
data, addr = sock.recvfrom(BUF_SIZE)
# sw = swc.StopAndWait(FILE_DEST,sock, addr, TIMEOUT)
# sw.recv_file()

ser = sr.SelectiveRepeat(FILE_DEST, sock, addr, TIMEOUT, 5)
ser.recv_file()