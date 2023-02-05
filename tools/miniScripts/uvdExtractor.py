# USAGE INSTRUCTIONS:
# 1. You need to have Nvidia Texture Tools Exporter installed. Make sure the nvttPath variable below is correct.
# 2. You need to have pillow installed. You can install it with "pip install pillow".
# 3. The .dat & .dtt must be extracted and the folders must be next to each other.
# 4. You can extract the .uvd either with drag & drop or by passing the path as the first argument.
#    Example: python uvdExtractor.py "C:\...\ui_core.dat\core.uvd"

import subprocess
from typing import BinaryIO
import os
from os.path import join, dirname, basename, splitext
import sys
import struct
from PIL import Image

nvttPath = "C:\\Program Files\\NVIDIA Corporation\\NVIDIA Texture Tools\\nvtt_export.exe"
uvdPath = sys.argv[1] if len(sys.argv) > 1 else "[FALLBACK PATH]"
fileBaseName = splitext(basename(uvdPath))[0]
datPath = dirname(uvdPath)
dttPath = datPath.replace(".dat", ".dtt")
wtaPath = join(datPath, f"{fileBaseName}.wta")
wtpPath = join(dttPath, f"{fileBaseName}.wtp")
ddsExtractPath = join(dttPath, "textures")
texIdToImage: dict[int, Image.Image] = {}

mustExistFiles = [nvttPath, uvdPath, dttPath, wtaPath, wtpPath]
hasMissingFiles = False
for path in mustExistFiles:
	if os.path.exists(path):
		continue
	print(f"Not found: {path}")
	hasMissingFiles = True
if hasMissingFiles:
	input("Press enter to exit...")
	sys.exit(1)

def read_uint32(file) -> int:
    entry = file.read(4)
    return struct.unpack('<I', entry)[0]

def read_float(file) -> float:
    entry = file.read(4)
    return struct.unpack('<f', entry)[0]

class WtaHeader:
	id: str
	unknown: int
	numTex: int
	offsetTextureOffsets: int
	offsetTextureSizes: int
	offsetTextureFlags: int
	offsetTextureIdx: int
	offsetTextureInfo: int

	def __init__(self, file: BinaryIO):
		self.id = file.read(4).decode('utf-8')
		self.unknown = read_uint32(file)
		self.numTex = read_uint32(file)
		self.offsetTextureOffsets = read_uint32(file)
		self.offsetTextureSizes = read_uint32(file)
		self.offsetTextureFlags = read_uint32(file)
		self.offsetTextureIdx = read_uint32(file)
		self.offsetTextureInfo = read_uint32(file)


def extractWtaWtp():
	print("Extracting wta and wtp files...")
	# read metadata from wta file
	with open(wtaPath, 'rb') as file:
		header = WtaHeader(file)
		file.seek(header.offsetTextureOffsets)
		textureOffsets = [read_uint32(file) for i in range(header.numTex)]
		file.seek(header.offsetTextureSizes)
		textureSizes = [read_uint32(file) for i in range(header.numTex)]
		file.seek(header.offsetTextureFlags)
		textureFlags = [read_uint32(file) for i in range(header.numTex)]
		file.seek(header.offsetTextureIdx)
		textureIdx = [read_uint32(file) for i in range(header.numTex)]

	# extract dds files from wtp file
	ddsFiles: list[str] = []
	os.makedirs(ddsExtractPath, exist_ok=True)
	with open(wtpPath, 'rb') as file:
		for i in range(header.numTex):
			file.seek(textureOffsets[i])
			dds = file.read(textureSizes[i])
			ddsFile = join(ddsExtractPath, f"{i}_{textureIdx[i]:08x}.dds")
			ddsFiles.append(ddsFile)
			if os.path.exists(ddsFile):
				continue
			with open(ddsFile, 'wb') as ddsFile:
				ddsFile.write(dds)
	
	print("Converting dds to png...")

	# convert dds files to png
	for i, ddsFile in enumerate(ddsFiles):
		pngFile = ddsFile.replace(".dds", ".png")
		if not os.path.exists(pngFile):
			print(f"Converting {i + 1}/{len(ddsFiles)} DDS to PNG", end="\r")
			try:
				img = Image.open(ddsFile)
				img.save(pngFile)
				texIdToImage[textureIdx[i]] = img
			except:
				print("\nUsing NVTT")
				convCmd = f"\"{nvttPath}\" -o \"{pngFile}\" \"{ddsFile}\""
				# os.system(convCmd)
				res = subprocess.run(convCmd, shell=True)
				if res.returncode != 0:
					raise Exception(f"Failed to convert {ddsFile} to PNG")

		# load image
		texIdToImage[textureIdx[i]] = Image.open(pngFile)
	

class UvdHeader:
	ui_1: int
	entriesCount: int
	entriesOffset: int
	texturesOffset: int

	def __init__(self, file: BinaryIO):
		self.ui_1 = read_uint32(file)
		self.entriesCount = read_uint32(file)
		self.entriesOffset = read_uint32(file)
		self.texturesOffset = read_uint32(file)
	
class UvdEntry:
	name: str
	id: int
	textureId: int
	x: float
	y: float
	width: float
	height: float
	widthInverse: float
	heightInverse: float

	def __init__(self, file: BinaryIO):
		self.name = file.read(64).decode('utf-8').rstrip('\0')
		self.id = read_uint32(file)
		self.textureId = read_uint32(file)
		self.x = read_float(file)
		self.y = read_float(file)
		self.width = read_float(file)
		self.height = read_float(file)
		self.widthInverse = read_float(file)
		self.heightInverse = read_float(file)

class UvdTexture:
	name: str
	id: int

	def __init__(self, file: BinaryIO):
		self.name = file.read(32).decode('utf-8').rstrip('\0')
		self.id = read_uint32(file)

def extractUvd():
	print("Extracting uvd files...")
	with open(uvdPath, 'rb') as file:
		header = UvdHeader(file)
		file.seek(header.entriesOffset)
		entries = [UvdEntry(file) for i in range(header.entriesCount)]
		
	extractDir = join(datPath, f"{fileBaseName}.uvd_extracted")
	os.makedirs(extractDir, exist_ok=True)

	for i, entry in enumerate(entries):
		print(f"Extracting {i + 1}/{len(entries)}", end="\r")
		image = texIdToImage[entry.textureId]
		image = image.crop((int(entry.x), int(entry.y), int(entry.x + entry.width), int(entry.y + entry.height)))
		image.save(join(extractDir, f"{i}_{entry.name}__{entry.id:08x}.png"))

	print(f"Extracted {len(entries)} images.")

def main():
	extractWtaWtp()
	print()
	extractUvd()
	print("Done :D")

if __name__ == "__main__":
	main()
