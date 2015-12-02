import packet_gen as pac_gen

class StopAndWait:
	def __init__(self,file_name) :
		self.gen = pac_gen.PacketGen(file_name)

	