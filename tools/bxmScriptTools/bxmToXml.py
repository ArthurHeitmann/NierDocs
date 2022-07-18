import os
import bxm
import sys
import xml.dom.minidom
import xml.etree.ElementTree as ET

bxmFiles = [f for f in sys.argv[1:] if not f.endswith('.xml')]
if len(bxmFiles) == 1 and len(sys.argv) >= 3:
	xmlFiles = sys.argv[2:]
else:
	xmlFiles = [os.path.splitext(f)[0] + '.xml' for f in bxmFiles]

for i, bxmFile in enumerate(bxmFiles):
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

	with open(xmlFiles[i], "w", encoding="utf-8") as f:
		f.write(xmlStr)
