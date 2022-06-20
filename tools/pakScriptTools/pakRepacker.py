from io import BufferedReader, BufferedWriter
import json
import os
import struct
import sys
import pathlib
from typing import List
import zlib

def writeUint32(file: BufferedWriter, value):
	file.write(struct.pack('<I', value))

class FileEntry:
	uncompressedSize: int
	offset: int
	unknown: int

	pakSize: int
	data: bytes
	compressedData: bytes
	compressedSize: int

	def __init__(self, file: BufferedReader, offset: int, unknown: int):
		self.uncompressedSize = os.fstat(file.fileno()).st_size
		self.offset = offset
		self.unknown = unknown
		self.data = file.read()
		paddingEndLength = (4 - (self.uncompressedSize % 4)) % 4
		self.pakSize = len(self.data) + paddingEndLength

		if self.uncompressedSize > 1024:
			self.compressedData = zlib.compress(self.data, 1)
			paddingEndLength = (4 - (len(self.compressedData) % 4)) % 4
			self.compressedSize = len(self.compressedData)
			self.pakSize = 4 + self.compressedSize + paddingEndLength
		else:
			self.compressedData = None
			self.compressedSize = -1

	def writeHeaderEntryToFile(self, file: BufferedWriter):
		writeUint32(file, self.uncompressedSize)
		writeUint32(file, self.offset)
		writeUint32(file, self.unknown)
	
	def writeFileEntryToFile(self, file: BufferedWriter):
		if self.compressedData:
			writeUint32(file, self.compressedSize)
			file.write(self.compressedData)
			paddingEndLength = (4 - (self.compressedSize % 4)) % 4
			file.write(bytes(paddingEndLength))
		else:
			file.write(self.data)
			paddingEndLength = (4 - (self.uncompressedSize % 4)) % 4
			file.write(bytes(paddingEndLength))

def repackPak(pakDir: str):
	infoJsonFile = os.path.join(pakDir, "pakInfo.json")
	with open(infoJsonFile, "r") as f:
		pakInfo = json.load(f)

	pakFileName = pathlib.Path(pakDir).parts[-1]
	pakFile = str(pathlib.Path(pakDir).parent.parent / pakFileName)

	with open(pakFile, "wb") as pakF:
		writeUint32(pakF, pakInfo["version"])

		filesOffset = len(pakInfo["files"]) * 12 + 0x4
		lastFileOffset = filesOffset
		fileEntries: List[FileEntry] = []
		for yaxFile in pakInfo["files"]:
			with (open(os.path.join(pakDir, yaxFile["name"]), "rb")) as yaxF:
				fileEntry = FileEntry(yaxF, lastFileOffset, yaxFile["unknown1"])
				fileEntries.append(fileEntry)
				fileEntry.writeHeaderEntryToFile(pakF)
				lastFileOffset += fileEntry.pakSize
		
		for fileEntry in fileEntries:
			fileEntry.writeFileEntryToFile(pakF)

	print(f"Pak file {pakFileName} created ({len(fileEntries)} file repacked)")


if __name__ == "__main__":
	extractedPakDirs = sys.argv[1:]

	for pakDir in extractedPakDirs:
		repackPak(pakDir)
