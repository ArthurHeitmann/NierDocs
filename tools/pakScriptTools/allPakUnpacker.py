import os
from pakExtractor import extractPakFile

searchPath = "D:\\delete\\mods\\na\\blender\\extracted"
fileExt = "pak"

extractedPakFiles = 0
for root, dirs, files in os.walk(searchPath):
	for file in files:
		if file.split(".")[-1] != fileExt:
			continue
		
		extractedPakFiles += 1
		
		extractPakFile(os.path.join(root, file), True)

		print(f"Extracted {file}")

print(f"Extracted {extractedPakFiles} pak files.")
