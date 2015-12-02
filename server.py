import socket 
import threading 
import random
import pickle
import packet as pac
import stop_wait as saw_class

def handler(packet, rec_addr,UDP_IP):
	print("Received packet from host ",rec_addr)
	print("cksum: ", packet.cksum)
	print("len: ", packet.len)
	print("seqno: ", packet.seqno)
	print("data: ", packet.data)

	print("Sending back ", t.getName())

	# acquire a vacant socket
	t_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	t_sock.bind((UDP_IP,0))
	t_port = t_sock.getsockname()[1]
	print("New socket created on port ",t_port)
	t_sock.sendto(bytes(str(t_port), 'UTF-8'),rec_addr)

	# assume a stop-and-wait instance is used
	saw = saw_class.StopAndWait(packet.data)

if __name__ == "__main__":

	UDP_IP = "127.0.0.1"
	UDP_PORT = 55555
	buf = 1024

	addr = (UDP_IP,UDP_PORT)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	sock.bind((addr))

	i = 0
	while 1:
		print("Server is listening for connections")
		packet, rec_addr = sock.recvfrom(buf)
		p = pickle.loads(packet)

		# thread.start_new_thread(handler, (packet,rec_addr))
		t = threading.Thread(target=handler,args=(p,rec_addr,UDP_IP,))
		t.setName(str(i))
		i = i+1
		t.start()

	serversocket.close()
