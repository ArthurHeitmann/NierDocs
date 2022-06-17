import bxm
import sys
import xml.dom.minidom
import xml.etree.ElementTree as ET

bxmFile = sys.argv[1]
xmlFile = sys.argv[2] if len(sys.argv) > 2 else f"{bxmFile}.xml"

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
