import bxm
import sys
import xml.etree.ElementTree as ET

xmlFile = sys.argv[1]
bxmFile = sys.argv[2] if len(sys.argv) > 2 else f"{xmlFile}.bxm"

xmlRoot = ET.parse(xmlFile).getroot()
bxm.xmlToBxm(xmlRoot, bxmFile)
