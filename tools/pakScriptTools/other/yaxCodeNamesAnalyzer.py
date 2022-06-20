import json
import os
from typing import Dict, Tuple
import xml.etree.ElementTree as ET

searchPath = "D:\\delete\\mods\\na\\blender\\extracted"
fileExt = "yax"
resultsPath = "./results.json"

# {
# 	[codeHex: str]: {
# 		codeHex: str,
# 		names: List[str],
# 		parents: List[str],
# 		encountered: int,
# 		files: List[str]
# 	}
# }
codeNames: Dict[str, Dict] = {}

def analyzeXml(root: ET.Element, filePath: str):
	parentMap = {c: p for p in tree.iter() for c in p}
	for code in root.findall(".//code"):
		parent = parentMap[code]
		codeHex = code.text
		codeData: Dict
		if codeHex not in codeNames:
			codeData = {
				"codeHex": codeHex,
				"names": [],
				"parents": [],
				"encountered": 0,
				"files": []
			}
			codeNames[codeHex] = codeData
		else:
			codeData = codeNames[codeHex]

		parentTag = parent.tag
		sibling = parent.find("name")
		if sibling is not None:
			if "eng" in sibling.attrib and sibling.attrib["eng"]:
				siblingName = sibling.attrib["eng"]
			else:
				siblingName = sibling.text
		else:
			siblingName = ""

		if parentTag not in codeData["parents"]:
			codeData["parents"].append(parentTag)
		if siblingName not in codeData["names"]:
			codeData["names"].append(siblingName)
		if filePath not in codeData["files"]:
			codeData["files"].append(filePath)

		codeData["encountered"] += 1

for root, dirs, files in os.walk(searchPath):
	for file in files:
		if file.split(".")[-1] != fileExt:
			continue
		
		yaxXml = os.path.join(root, file.replace(".yax", ".xml"))
		if not os.path.exists(yaxXml):
			continue

		tree = ET.parse(yaxXml, ET.XMLParser(encoding="utf-8"))
		analyzeXml(tree.getroot(), yaxXml.replace(searchPath, ""))


with open(resultsPath, "w", encoding="utf-8") as f:
	jsonStr = json.dumps(codeNames, indent=4, ensure_ascii=False)
	f.write(jsonStr)
	print(f"Saved results to {resultsPath}")
