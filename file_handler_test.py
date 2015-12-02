from file_handler import File_handler

my_file = File_handler('/home/abuemeira/workspace/Networks-Assignment-2/RDT_Over_UDP/test.txt', 2)
byte_array = my_file.get_next_chunk()
print(byte_array)
while 1:
	byte_array = my_file.get_next_chunk()
	if not byte_array:
		break
	print(byte_array)
