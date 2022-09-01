import os
import struct
import json

filepath = "D:\\delete\\mods\\na\\blender\\extracted\\data009.cpk_unpacked\\txtmess\\nier2blender_extracted\\txt_core_us.dat\\txt_core.tmd"
outJsonFile = "tmd.json"

def read_uint32(f):
	return struct.unpack("<I", f.read(4))[0]

def read_str(f, length):
	return f.read(length * 2).decode("utf-16-le").rstrip("\0")

"""
struct Entry {
	uint32 idSize;
	wchar_t id[idSize];
	uint32 textSize;
	wchar_t text[textSize];
};
"""
def readEntry(f):
	idSize = read_uint32(f)
	id = read_str(f, idSize)
	textSize = read_uint32(f)
	text = read_str(f, textSize)
	return id, text

tmdDict = {}
with open(filepath, "rb") as f:
	count = read_uint32(f)
	fileSie = os.path.getsize(filepath)
	while f.tell() + 8< fileSie:
		id, text = readEntry(f)
		tmdDict[id] = text

with open(outJsonFile, "w", encoding="utf-8") as f:
	json.dump(tmdDict, f, ensure_ascii=False, indent=4)
