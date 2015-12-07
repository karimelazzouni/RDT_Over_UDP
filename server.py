import socket 
import threading 
import random
import pickle
import packet as pac
import stop_wait_server as sws
import selective_repeat_server as sr

def handler(packet, rec_addr,SERVER_IP,TIMEOUT,P_LOSS,MAX_WINDOW):
	print("Received packet from host ",rec_addr)
	print("Acquiring new vacant socket")
	# acquire a vacant socket
	t_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	t_sock.bind((SERVER_IP,0))
	t_port = t_sock.getsockname()[1]
	print("New socket created on port ",t_port)
	t_sock.sendto(pickle.dumps(t_port),rec_addr)

	# assume a stop-and-wait instance is used
	# saw = sws.StopAndWait(packet.data, t_sock, rec_addr, TIMEOUT,P_LOSS)
	# saw.send()

	ser = sr.SelectiveRepeat(packet.data, t_sock, rec_addr, TIMEOUT, P_LOSS, MAX_WINDOW)
	ser.send_file()

	print("Done sending, destroying connection")
	t_sock.close()

def read_in(file_name) :
	with open(file_name) as f :
		SERVER_PORT = int(f.readline())
		MAX_WINDOW = int(f.readline())
		P_LOSS = float(f.readline())
		TIMEOUT = int(f.readline())
	return (SERVER_PORT,MAX_WINDOW,P_LOSS,TIMEOUT)
		


if __name__ == "__main__":

	BUF_SIZE = 4096
	SERVER_IP = "127.0.0.1"
	(SERVER_PORT,MAX_WINDOW,P_LOSS,TIMEOUT) = read_in("/tmp/server/server.in")

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((SERVER_IP,SERVER_PORT))

	i = 0
	while 1:
		print("Server is listening for connections")
		print("IP\t: ",SERVER_IP)
		print("PORT\t: ",SERVER_PORT)
		packet, rec_addr = sock.recvfrom(BUF_SIZE)
		p = pickle.loads(packet)

		t = threading.Thread(target=handler,args=(p,rec_addr,SERVER_IP,TIMEOUT,P_LOSS,MAX_WINDOW,))
		t.setName(str(i))
		i = i+1
		t.start()

	sock.close()