# file io

import struct


def read_int8(file) -> int:
	entry = file.read(1)
	return struct.unpack("<b", entry)[0]

def read_uint8(file) -> int:
	entry = file.read(1)
	return struct.unpack('<B', entry)[0]

def read_uint16(file) -> int:
	entry = file.read(2)
	return struct.unpack('<H', entry)[0]

def read_uint16_be(file) -> int:
	entry = file.read(2)
	return struct.unpack('>H', entry)[0]

def read_int16(file) -> int:
	entry = file.read(2)
	return struct.unpack('<h', entry)[0]

def read_uint32(file) -> int:
	entry = file.read(4)
	return struct.unpack('<I', entry)[0]

def read_int32(file) -> int:
	entry = file.read(4)
	return struct.unpack('<i', entry)[0]

def read_char(file) -> str:
	entry = file.read(1)
	return struct.unpack('<c', entry)[0]

def read_float(file) -> float:
	entry = file.read(4)
	return struct.unpack('<f', entry)[0]

def read_string(file, maxLen = -1) -> str:
	binaryString = b""
	while maxLen == -1 or len(binaryString) < maxLen:
		char = read_char(file)
		if char == b'\x00':
			break
		binaryString += char
	return binaryString.decode('utf-8')

signMask = 0x8000
expoMask = 0x7e00
mantMask = 0x01ff
inf = float("inf")
ninf = float("-inf")
nan = float("nan")
def read_PgHalf(file) -> float:
    pghalf = read_uint16(file)
    
    sign = pghalf & signMask
    expo = pghalf & expoMask
    mant = pghalf & mantMask
    
    expo >>= 9
    
    if expo == 0 and mant == 0:
        return 0.0
    if expo == 63:
        if mant == 0:
            return ninf if sign else inf
        else:
            return nan
    
    expo -= 47
    sign <<= 16
    expo += 127
    expo <<= 23
    mant <<= 14
    
    flBytes = sign | expo | mant
    
    fl = struct.unpack("f", struct.pack("I", flBytes))[0]
    
    return fl

def writeBe_float(file, float):
	entry = struct.pack('<f', float)
	file.write(entry)

def writeBe_char(file, char):
	entry = struct.pack('<s', bytes(char, 'utf-8'))
	file.write(entry)

def writeBe_int32(file, int):
	entry = struct.pack('<i', int)
	file.write(entry)

def writeBe_uint32(file, int):
	entry = struct.pack('<I', int)
	file.write(entry)

def writeBe_int16(file, int):
	entry = struct.pack('<h', int)
	file.write(entry)

def writeBe_uint16(file, int):
	entry = struct.pack('<H', int)
	file.write(entry)

def writeBe_byte(file, val):
	entry = struct.pack('B', val)
	file.write(entry)

def writeBe_float16(file, val):
	entry = struct.pack("<e", val)
	file.write(entry)