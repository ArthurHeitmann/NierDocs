import os
import time
from typing import List, Tuple

searchPath = "[ENTER YOUR SEARCH DIRECTORY HERE]" # make sure to escape backslashes
searchStr = "SendCommand"
strEncoding = "utf-8"
isCaseSensitive = False
fileExt = ["xml"]


if not isCaseSensitive:
	searchStr = searchStr.lower()

# iterate over all files in the search path
# and search for the search string, byte by byte
t1 = time.time()
foundOccurrences = 0
for root, dirs, files in os.walk(searchPath):
	for file in files:
		if file.split(".")[-1] not in fileExt:
			continue
		foundLines: List[Tuple[int, str]] = []
		with open(os.path.join(root, file), "rb") as f:
			line = f.readline().decode(strEncoding, "ignore")
			lineNum = 1
			while line:
				cmpLine = line if isCaseSensitive else line.lower()
				if searchStr in cmpLine:
					foundLines.append((lineNum, line))
					foundOccurrences += 1
				line = f.readline().decode(strEncoding, "ignore")
				lineNum += 1

		if len(foundLines) > 0:
			displayPath = os.path.join(root, file).replace(searchPath, "")
			print(f"In {displayPath}:")
			for lineNum, line in foundLines:
				print(f"{lineNum:4d}: {line}", end="")
			print("-" * 80)
			

elapsed = time.time() - t1

print(f"Found {foundOccurrences} occurrences in {elapsed} seconds")