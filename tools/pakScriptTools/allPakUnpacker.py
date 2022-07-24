import os
import sys
from pakExtractor import extractPakFile

fallbackPath = "D:\\delete\\mods\\na\\blender\\extracted"
searchPath = sys.argv[1] if len(sys.argv) > 1 else fallbackPath
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
