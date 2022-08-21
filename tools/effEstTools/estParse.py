from io import BufferedWriter
import os
import struct
from typing import List

def read_uint32(file: BufferedWriter) -> int:
	entry = file.read(4)
	return struct.unpack('<I', entry)[0]

def read_uint16(file: BufferedWriter) -> int:
	entry = file.read(2)
	return struct.unpack('<H', entry)[0]

def write_uint32(file: BufferedWriter, value: int) -> None:
	file.write(struct.pack('<I', value))

def write_uint16(file: BufferedWriter, value: int) -> None:
	file.write(struct.pack('<H', value))

def align16Bytes(val: int) -> int:
	return (val + 0xF) & ~0xF
estPath = "[FILL THIS PATH]\\data010.cpk_unpacked\\effect\\nier2blender_extracted\\ba0601.eff\\001.bak"
estOutPath = "[FILL THIS PATH]\\data010.cpk_unpacked\\effect\\nier2blender_extracted\\ba0601.eff\\001.est"

class EstHeader:
	id: str
	recordCount: int
	recordOffsetsOffset: int
	typesOffset: int
	typesEndOffset: int
	typesSize: int
	typesNumber: int

	def __init__(self, file: BufferedWriter):
		self.id = file.read(4).decode("ascii")
		self.recordCount = read_uint32(file)
		self.recordOffsetsOffset = read_uint32(file)
		self.typesOffset = read_uint32(file)
		self.typesEndOffset = read_uint32(file)
		self.typesSize = read_uint32(file)
		self.typesNumber = read_uint32(file)
	
	def write(self, file: BufferedWriter) -> None:
		file.write(self.id.encode("ascii"))
		write_uint32(file, self.recordCount)
		write_uint32(file, self.recordOffsetsOffset)
		write_uint32(file, self.typesOffset)
		write_uint32(file, self.typesEndOffset)
		write_uint32(file, self.typesSize)
		write_uint32(file, self.typesNumber)

class EstType:
	u_a: int
	id: str
	size: int
	offset: int

	def __init__(self, file: BufferedWriter):
		self.u_a = read_uint32(file)
		self.id = file.read(4).decode("ascii")
		self.size = read_uint32(file)
		self.offset = read_uint32(file)
	
	def write(self, file: BufferedWriter):
		write_uint32(file, self.u_a)
		file.write(self.id.encode("ascii"))
		write_uint32(file, self.size)
		write_uint32(file, self.offset)

class EstRecordSection:
	type: EstType
	data: bytes

	def __init__(self, file: BufferedWriter, type: EstType):
		self.type = type
		self.data = file.read(type.size)
	
	def write(self, file: BufferedWriter):
		file.write(self.data)
	
class EstRecord:
	allTypeGroups: List[EstType]
	sections: List[EstRecordSection]

	def __init__(self, file: BufferedWriter, allTypeGroups: List[EstType]):
		self.allTypeGroups = allTypeGroups[:]
		self.sections = []
		recordPos = file.tell()
		for typeGroup in self.allTypeGroups:
			if typeGroup.size == 0:
				continue # TODO remove
			file.seek(recordPos + typeGroup.offset)
			self.sections.append(EstRecordSection(file, typeGroup))
	
	def write(self, file: BufferedWriter):
		startPos = file.tell()
		for section in self.sections:
			file.seek(startPos + section.type.offset)
			section.write(file)

	def updateTypeOffsets(self) -> int:
		usedGroups = [section.type.id for section in self.sections]
		for group in self.allTypeGroups:
			if group.id not in usedGroups:
				group.size = 0
				group.offset = 0
		prevOffset = 0
		for i, section in enumerate(self.sections):
			self.sections[i].type.offset = prevOffset
			prevOffset += section.type.size
		
		return prevOffset

class Est:
	header: EstHeader
	recordsOffsets: List[int]
	records: List[EstRecord]

	def __init__(self, file: BufferedWriter):
		self.header = EstHeader(file)
		
		file.seek(self.header.recordOffsetsOffset)
		self.recordsOffsets = []
		for i in range(self.header.recordCount):
			self.recordsOffsets.append(read_uint32(file))

		file.seek(self.header.typesOffset)
		typeGroups = []
		for i in range(self.header.recordCount):
			typeGroup = []
			for j in range(self.header.typesNumber):
				typeGroup.append(EstType(file))
			typeGroups.append(typeGroup)
		
		self.records = []
		for i in range(self.header.recordCount):
			file.seek(self.recordsOffsets[i])
			self.records.append(EstRecord(file, typeGroups[i]))

	def updateOffsets(self) -> None:
		headerSize = 0x1c
		offsetsOffset = align16Bytes(headerSize)
		recordsCount = len(self.records)
		offsetsSize = recordsCount * 4
		typesOffset = align16Bytes(offsetsOffset + offsetsSize)
		recordsOffset = align16Bytes(typesOffset + recordsCount * 27 * 16)
		self.header.recordCount = recordsCount
		self.header.recordOffsetsOffset = offsetsOffset
		self.header.typesOffset = typesOffset
		self.header.typesEndOffset = recordsOffset

		self.recordsOffsets = []
		lastOffset = recordsOffset
		for record in self.records:
			recordSize = record.updateTypeOffsets()
			self.recordsOffsets.append(lastOffset)
			lastOffset += recordSize
	
	def write(self, file: BufferedWriter) -> None:
		file.seek(0)
		self.header.write(file)

		file.seek(self.header.recordOffsetsOffset)
		for offset in self.recordsOffsets:
			write_uint32(file, offset)

		file.seek(self.header.typesOffset)
		for record in self.records:
			for typeGroup in record.allTypeGroups:
				typeGroup.write(file)
			
		for i, record in enumerate(self.records):
			file.seek(self.recordsOffsets[i])
			record.write(file)

	
with open(estPath, "rb") as estFile:
	est = Est(estFile)


# DO YOUR EDITS HERE

# est.records = [est.records[0], est.records[1], ]


# END

est.updateOffsets()
with open(estOutPath, "wb") as outFile:
	est.write(outFile)
