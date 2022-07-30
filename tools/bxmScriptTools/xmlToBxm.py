import os
import bxm
import sys
import xml.etree.ElementTree as ET

xmlFiles = [f for f in sys.argv[1:] if f.endswith('.xml')]
if len(xmlFiles) == 1 and len(sys.argv) >= 3:
	bxmFiles = sys.argv[2:]
else:
	bxmFiles = [os.path.splitext(f)[0] + '.bxm' for f in xmlFiles]

for i, xmlFile in enumerate(xmlFiles):
	xmlRoot = ET.parse(xmlFile).getroot()
	bxm.xmlToBxm(xmlRoot, bxmFiles[i])
