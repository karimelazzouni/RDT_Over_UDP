from file_handler import File_handler

my_file = File_handler('/tmp/test', 500)
while 1:
	byte_array = my_file.get_next_chunk()
	if not byte_array:
		break
	print(byte_array)
	print ("done ",len(byte_array))
