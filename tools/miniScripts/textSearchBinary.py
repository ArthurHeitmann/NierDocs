import os
from time import time

searchPath = "[ENTER YOUR SEARCH DIRECTORY HERE]" # make sure to escape backslashes
searchStr = "SendCommand"
strEncoding = "utf-8"
# strEncoding = "shift-jis"
searchBytes = searchStr.encode(strEncoding)
fileExt = ["xml"]

# iterate over all files in the search path
# and search for the search string, byte by byte
t1 = time()
foundOccurrences = 0
for root, dirs, files in os.walk(searchPath):
	for file in files:
		if file.split(".")[-1] not in fileExt:
			continue
		with open(os.path.join(root, file), "rb") as f:
			fileBytesLen = os.path.getsize(os.path.join(root, file))
			byteI = 0
			while byteI + len(searchBytes) <= fileBytesLen:
				if f.read(len(searchBytes)) == searchBytes:
					print(f"file: {os.path.join(root, file).replace(searchPath, '')}, byte: {byteI} / {hex(byteI)}")
					foundOccurrences += 1
					byteI += len(searchBytes)
				else:
					byteI += 1
				f.seek(byteI)
td = time() - t1

print("Found " + str(foundOccurrences) + " occurrences in " + str(td) + " seconds.")
