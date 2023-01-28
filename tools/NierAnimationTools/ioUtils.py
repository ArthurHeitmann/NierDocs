import struct

# read

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

# write

def write_int8(file, value: int) -> None:
	entry = struct.pack("<b", value)
	file.write(entry)

def write_uint8(file, value: int) -> None:
	entry = struct.pack('<B', value)
	file.write(entry)

def write_uint16(file, value: int) -> None:
	entry = struct.pack('<H', value)
	file.write(entry)

def write_uint16_be(file, value: int) -> None:
	entry = struct.pack('>H', value)
	file.write(entry)

def write_int16(file, value: int) -> None:
	entry = struct.pack('<h', value)
	file.write(entry)

def write_uint32(file, value: int) -> None:
	entry = struct.pack('<I', value)
	file.write(entry)

def write_int32(file, value: int) -> None:
	entry = struct.pack('<i', value)
	file.write(entry)

def write_char(file, value: str) -> None:
	entry = struct.pack('<c', value)
	file.write(entry)

def write_float(file, value: float) -> None:
	entry = struct.pack('<f', value)
	file.write(entry)

def write_string(file, value: str, maxLen = -1) -> None:
	binaryString = value.encode('utf-8')
	if maxLen != -1:
		binaryString = binaryString[:maxLen]
	file.write(binaryString)
	if maxLen == -1:
		file.write(b'\x00')

def write_PgHalf(file, value: float) -> None:
	if value == 0.0:
		write_uint16(file, 0)
		return
	flBytes = struct.unpack("I", struct.pack("f", value))[0]

	if value == inf:
		sign = 0
		expo = 0x7e00
		mant = 0
	elif value == ninf:
		sign = 0x8000
		expo = 0x7e00
		mant = 0
	else:
		sign = flBytes & 0x80000000
		expo = flBytes & 0x7f800000
		mant = flBytes & 0x007fffff
		
		sign >>= 16
		expo >>= 23
		expo -= 127
		expo += 47
		expo <<= 9
		mant >>= 14
	
	pghalf = sign | expo | mant
	
	write_uint16(file, pghalf)
