# Current usage: put all files you want included in the .dat into the "files" array below, run, and put the .metadata files into the extracted dat folder. Then export with the N2B2N addon.

import struct
from typing import List
import zlib

def toUint32(value: int) -> bytes:
	return struct.pack('<I', value)

def toInt16(value: int) -> bytes:
	return struct.pack('<h', value)

def crc32(text: str) -> int:
	return zlib.crc32(text.encode('ascii')) & 0xFFFFFFFF

def next_power_of_2_bits(x: int) -> int:  
    return 1 if x == 0 else (x - 1).bit_length()

hashDataOutFile = "./hash_data.metadata"
fileOrderOutFile = "./file_order.metadata"

files = [
	"Pl0010AtkCombo.csv",
	"hackingInfo.csv",
	"pl0000BaseInfo.csv",
	"pl0000ExpInfo.csv",
	"pl000d.sop",
	"pl000d.wta",
	"pl000d_0_0_clh.bxm",
	"pl000d_0_0_clp.bxm",
	"pl000d_0_0_clw.bxm",
	"pl000d_0_1_clh.bxm",
	"pl000d_0_1_clp.bxm",
]
files.sort(key=lambda x: x.lower())

class HashData:
	preHashShift: int
	bucketOffsets: List[int]
	hashes: List[int]
	fileIndices: List[int]

	def __init__(self, preHashShift: int):
		self.preHashShift = preHashShift
		self.bucketOffsets = []
		self.hashes = []
		self.fileIndices = []
	
	def write(self, file):
		bucketsOffset = 4*4
		hashesOffset = bucketsOffset + len(self.bucketOffsets)*2
		fileIndicesOffset = hashesOffset + len(self.hashes)*4
		
		file.write(toUint32(self.preHashShift))
		file.write(toUint32(bucketsOffset))
		file.write(toUint32(hashesOffset))
		file.write(toUint32(fileIndicesOffset))
		for bucketOffset in self.bucketOffsets:
			file.write(toInt16(bucketOffset))
		for hash in self.hashes:
			file.write(toUint32(hash))
		for fileIndex in self.fileIndices:
			file.write(toUint32(fileIndex))

class FileOrder:
	files: List[str]

	def __init__(self):
		self.files = []
	
	def write(self, file):
		maxLen = max(map(len, self.files)) + 1
		file.write(toUint32(len(self.files)))
		file.write(toUint32(maxLen))
		for fileName in self.files:
			file.write(fileName.encode('ascii'))
			# fill remaining space with null bytes
			file.write(b'\x00'*(maxLen - len(fileName)))
		

def generateHashData() -> bytes:
	preHashShift = 32 - next_power_of_2_bits(len(files))
	bucketOffsetsSize = 1 << (31 - preHashShift)
	bucketOffsets = [-1] * bucketOffsetsSize
	hashes = [0] * len(files)
	fileIndices = list(range(len(files)))
	fileNames = files.copy()

	# generate hashes
	for i in range(len(files)):
		fileName = files[i]
		hash = crc32(fileName.lower())
		otherHash = (hash & 0x7FFFFFFF)
		hashes[i] = otherHash
	# sort by first half byte (x & 0x70000000)
	# sort indices & hashes at the same time
	hashes, fileIndices, fileNames = zip(*sorted(zip(hashes, fileIndices, fileNames), key=lambda x: x[0] & 0x70000000))
	# generate bucket list
	for i in range(len(files)):
		bucketOffsetsIndex = hashes[i] >> preHashShift
		if bucketOffsets[bucketOffsetsIndex] == -1:
			bucketOffsets[bucketOffsetsIndex] = i
	

	# print bucket offsets, hashes, fileIndeces
	for i in range(len(bucketOffsets)):
		print(f"{i}: {bucketOffsets[i]}")
	for i in range(len(hashes)):
		print(f"{i}: 0x{hashes[i]:08X}")
	for i in range(len(fileIndices)):
		print(f"{i}: {fileIndices[i]}")
	
	hashData = HashData(preHashShift)
	hashData.bucketOffsets = bucketOffsets
	hashData.hashes = hashes
	hashData.fileIndices = fileIndices
	fileOrder = FileOrder()
	fileOrder.files = fileNames

	with open(hashDataOutFile, "wb") as file:
		hashData.write(file)
	with open(fileOrderOutFile, "wb") as file:
		fileOrder.write(file)

if __name__ == "__main__":
	generateHashData()

	print("Done!")
