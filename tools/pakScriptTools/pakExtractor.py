from io import BufferedReader
import json
import os
import struct
import sys
import pathlib
from typing import List
import zlib

def read_uint32(file) -> int:
	entry = file.read(4)
	return struct.unpack('<I', entry)[0]

class HeaderEntry:
	uncompressedSize: int
	offset: int
	unknown: int

	pakSize: int

	def __init__(self, file: BufferedReader):
		self.uncompressedSize = read_uint32(file)
		self.offset = read_uint32(file)
		self.unknown = read_uint32(file)

class FilEntry:
	data: bytes

	isCompressed: bool

	def __init__(self, file: BufferedReader, entrySize: int, uncompressedSize: int, isCompressed: bool):
		self.isCompressed = isCompressed
		
		if isCompressed:
			compressedSize = read_uint32(file)
			paddingEndLength = entrySize - compressedSize - 4
		else:
			paddingEndLength = (4 - (uncompressedSize % 4)) % 4

		self.data = file.read(entrySize - paddingEndLength)

pakFile = sys.argv[1] if len(sys.argv) > 1 else "D:\\delete\\mods\\na\\blender\\extracted\\data012.cpk_unpacked\\st5\\nier2blender_extracted\\r501.dat\\r501_hap.pak"

with open(pakFile, "rb") as f:
	fileSize = os.fstat(f.fileno()).st_size
	f.seek(0x8)
	firstOffset = read_uint32(f)
	fileCount = (firstOffset - 0x4) // 12
	
	f.seek(0)
	version = read_uint32(f)
	# gather entries
	headerEntries: List[HeaderEntry] = []
	for i in range(fileCount):
		headerEntries.append(HeaderEntry(f))
	
	# calculate files sizes
	lastOffset = firstOffset
	for i in range(1, fileCount):
		headerEntries[i - 1].pakSize = headerEntries[i].offset - lastOffset
		lastOffset = headerEntries[i].offset
	headerEntries[fileCount - 1].pakSize = fileSize - lastOffset

	# read files
	files: List[FilEntry] = []
	for i in range(fileCount):
		f.seek(headerEntries[i].offset)
		isCompressed = headerEntries[i].uncompressedSize > headerEntries[i].pakSize
		files.append(FilEntry(f, headerEntries[i].pakSize, headerEntries[i].uncompressedSize, isCompressed))

	# write files
	extractionFolder = os.path.join(os.path.dirname(pakFile), "pakExtracted", os.path.basename(pakFile))
	pathlib.Path(extractionFolder).mkdir(parents=True, exist_ok=True)

	pakInfoJson = {
		"version": version,
		"files": [
			{
				"name": f"{i}.yax",	# yax, cause Yet Another Xml encoding
				"unknown1": headerEntries[i].unknown,
			}
			for i in range(fileCount)
		]
	}
	with open(os.path.join(extractionFolder, "pakInfo.json"), "w") as f:
		f.write(json.dumps(pakInfoJson, indent=4))
	
	for i in range(fileCount):
		data: bytes
		if files[i].isCompressed:
			data = zlib.decompress(files[i].data)
		else:
			data = files[i].data

		with open(os.path.join(extractionFolder, f"{i}.yax"), "wb") as f:
			f.write(data)
		print(f"Extracted file {i}.yax")

	print("Extraction complete")

