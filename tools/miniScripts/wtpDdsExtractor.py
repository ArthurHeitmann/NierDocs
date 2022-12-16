import os
from os import path
import sys

def extractDds(wtpPath: str):
	with open(wtpPath, "rb") as f:
		bytes = f.read()

	start = bytes.find(b"DDS ")
	i = 0
	while True:
		nextDds = bytes.find(b"DDS ", start + 1)
		if nextDds == -1:
			nextDds = len(bytes)
		outName = path.join(path.dirname(wtpPath), f"{path.basename(wtpPath)}_{i}.dds")
		with open(outName, "wb") as f:
			f.write(bytes[start:nextDds])
		if nextDds == len(bytes):
			break
		start = nextDds
		i += 1

wtpFiles = sys.argv[1:]
for wtpFile in wtpFiles:
	try:
		print("Extracting", path.basename(wtpFile))
		extractDds(wtpFile)
	except Exception as e:
		print(f"Failed to extract {wtpFile}: {e}")
