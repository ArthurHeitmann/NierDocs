# used for generating 25.xml in core_hap.pak

import os
import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom

inTextFile = sys.argv[1] if len(sys.argv) > 1 else "C:\\Fallback\\Or\\Debug\\Path.txt"
outXmlFile = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(inTextFile)[0] + ".xml"

with open(inTextFile, "rb") as f:
	textBytes = f.read()

hexString = textBytes.hex()
MAX_CHUNK_SIZE = 64
strChunksCount = len(hexString) // MAX_CHUNK_SIZE + 1
strChunks = [hexString[i * MAX_CHUNK_SIZE : (i + 1) * MAX_CHUNK_SIZE] for i in range(strChunksCount)]

root = ET.Element("root")
ET.SubElement(root, "id").text = "0x75445849"
ET.SubElement(root, "name").text = "CharName"
ET.SubElement(root, "priority").text = "100"
ET.SubElement(root, "attribute").text = "0x4"
ET.SubElement(root, "group").text = "0xdfb40ba8"
text = ET.SubElement(root, "text")
ET.SubElement(text, "size").text = f"0x{len(textBytes):x}"
for i in range(strChunksCount):
	ET.SubElement(text, "value").text = strChunks[i]

xmlStr = xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml(indent="\t", encoding="utf-8")
with open(outXmlFile, "wb") as f:
	f.write(xmlStr)

print("Done")

