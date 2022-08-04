import os
from pydoc import isdata
import bxm
import sys
import xml.dom.minidom
import xml.etree.ElementTree as ET

bxmFiles = [f for f in sys.argv[1:] if not f.endswith('.xml')]
if len(bxmFiles) == 1 and len(sys.argv) >= 3:
	xmlFiles = sys.argv[2:]
else:
	xmlFiles = [os.path.splitext(f)[0] + '.xml' for f in bxmFiles]

def bxmToXml(bxmFile, xmlFile):
	xmlResult = bxm.bxmToXml(bxmFile)
	try:
		xmlStr = ET.tostring(xmlResult.toXml())
		if type(xmlStr) == bytes:
			xmlStr = xmlStr.decode("utf-8")
		dom = xml.dom.minidom.parseString(xmlStr)
		xmlStr = dom.toprettyxml(indent="\t")
	except:
		print("Warning: using fallback string representation")
		xmlStr = str(xmlResult)

	with open(xmlFile, "w", encoding="utf-8") as f:
		f.write(xmlStr)

for i, bxmFile in enumerate(bxmFiles):
	if os.path.isdir(bxmFile):
		print(f"processing folder {bxmFile}...")
		for root, dirs, files in os.walk(bxmFile):
			for file in files:
				if file.endswith('.bxm'):
					bxmToXml(os.path.join(root, file), os.path.join(root, os.path.splitext(file)[0] + '.xml'))
	else:
		bxmToXml(bxmFile, xmlFiles[i])