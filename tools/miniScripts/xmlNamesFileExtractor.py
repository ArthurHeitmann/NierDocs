# used for extracting the text from 25.xml in core_hap.pak

import os
import sys
import xml.etree.ElementTree as ET

xmlPath = sys.argv[1] if len(sys.argv) > 1 else "C:\\Fallback\\Or\\Debug\\Path.xml"
outPath = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(xmlPath)[0] + ".txt"

xml = ET.parse(xmlPath)
root = xml.getroot()
textEl = root.find("text")
hexStr = "".join([c.text for c in textEl.findall("value")])
decodedBytes = bytes.fromhex(hexStr)

with open(outPath, "wb") as f:
	f.write(decodedBytes)
