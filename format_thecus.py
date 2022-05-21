import struct
import sys

write_string_msg = 0x11

def send(msg_code, msg, msg_id = 1):
	
	new_msg = bytearray([msg_code])
	new_msg.extend(msg)
	
	print(struct.pack('>ccH%dsc' % len(new_msg), b'\x02', b'\x01',
		len(new_msg), new_msg, b'\x03'))


def write_message(msg1, msg2, msg_id = 1):
	str_msg = '{0:40.40}{1:20.20}'.format(msg1, msg2)
	send(write_string_msg, str_msg.encode('ascii'), msg_id)

if __name__ == '__main__':
	try:
		msg1 = sys.argv[1]
	except Exception:
		msg1 = "Hello World"
	try:
		msg2 = sys.argv[2]
	except Exception:
		msg2 = ""

	try:
		write_message(msg1, msg2)
	except Exception as e:
		print(e)

