import packet as class_packet
import file_handler as hand
import random
import sys

class PacketGen:
	CHUNK_SIZE = 500

	def __init__(self, file_name=None) :
		self.init_seqno = ((random.randint(0,sys.maxsize)%100)+1) # randomly generated sequence number
		self.next_seqno = self.init_seqno
		if not file_name == None :
			self.file_name = file_name
			self.file_is_reg = 1 # boolean that indicates sys.maxsizethat a file was assigned to this PacketGenerator
			self.f_handler = hand.File_handler(self.file_name, self.CHUNK_SIZE)
		else :
			self.file_is_reg = 0

	def gen_cksum(self,s) :
		binary_s = ' '.join(format(ord(x), 'b').zfill(8) for x in s)
		byte_array = binary_s.split()
		total_sum = 0
		for i in range(0, len(byte_array)-1,2) :
			first_int = int(byte_array[i],2)
			second_int = int(byte_array[i+1],2)
			sum = first_int + second_int
			if sum > 255 :
				sum = sum - 256
				sum = sum + 1
			total_sum = total_sum + sum
			if total_sum > 255 :
				total_sum = total_sum - 256
				total_sum = total_sum + 1
		if (len(byte_array)%2 == 1) : # special case for odd 
			last_int = int(byte_array[len(byte_array)-1],2)
			total_sum = last_int + total_sum
			if total_sum > 255 :
				total_sum = total_sum - 256
				total_sum = total_sum + 1
		total_sum = total_sum^255
		#cksum = '{0:08b}'.format(total_sum)
		return total_sum

	def gen_packet(self,data_string) :
		packet = class_packet.Packet(self.gen_cksum(data_string),(len(data_string)*8+12),self.next_seqno,data_string)
		self.next_seqno = self.next_seqno + 1
		return packet

	def gen_close_packet(self) :
		packet = class_packet.Packet(0,12,0,"")
		return packet

	def gen_packet_from_file(self) : # returns None if file was not registered to the PacketGen at the construction time
									 # check by "if <return> is not None : <file was registered at construction time> "
		if self.file_is_reg == 0 :
			return None
		data_bytes = self.f_handler.get_next_chunk()
		if not data_bytes :
			return None 
		packet = class_packet.Packet(self.gen_cksum(data_bytes),len(data_bytes)+12,self.next_seqno,data_bytes)
		self.next_seqno = self.next_seqno + 1
		return packet

# gen = PacketGen("/tmp/test")
# packet = gen.gen_packet_from_file()
# if packet is not None :  
# 	print (packet.len)
# else :
# 	print ("error: file not specified")
# packet = gen.gen_packet_from_file()
# if packet is not None :  
# 	print (packet.len)
# else :
# 	print ("error: file not specified")

