import struct

# file io

def readBe_uint8(file) -> int:
	entry = file.read(1)
	return struct.unpack('B', entry)[0]

def readBe_uint16(file) -> int:
	entry = file.read(2)
	return struct.unpack('>H', entry)[0]

def readBe_int16(file) -> int:
	entry = file.read(2)
	return struct.unpack('>h', entry)[0]

def readBe_uint32(file) -> int:
	entry = file.read(4)
	return struct.unpack('>I', entry)[0]

def readBe_int32(file) -> int:
	entry = file.read(4)
	return struct.unpack('>i', entry)[0]

def readBe_char(file) -> str:
	entry = file.read(1)
	return struct.unpack('>c', entry)[0]

def readBe_string(file, maxBen = -1) -> str:
	binaryString = b""
	while maxBen == -1 or len(binaryString) > maxBen:
		char = readBe_char(file)
		if char == b'\x00':
			break
		binaryString += char
	try:
		return binaryString.decode('utf-8')
	except:
		try:
			return binaryString.decode('shift-jis')
		except:
			print("Error: could not decode string", binaryString)
			return str(binaryString)

def writeBe_float(file, float):
	entry = struct.pack('>f', float)
	file.write(entry)

def writeBe_char(file, char):
	entry = struct.pack('>s', bytes(char, 'utf-8'))
	file.write(entry)

def writeBe_int32(file, int):
	entry = struct.pack('>i', int)
	file.write(entry)

def writeBe_uint32(file, int):
	entry = struct.pack('>I', int)
	file.write(entry)

def writeBe_int16(file, int):
	entry = struct.pack('>h', int)
	file.write(entry)

def writeBe_uint16(file, int):
	entry = struct.pack('>H', int)
	file.write(entry)

def writeBe_byte(file, val):
	entry = struct.pack('B', val)
	file.write(entry)

def writeBe_float16(file, val):
	entry = struct.pack(">e", val)
	file.write(entry)