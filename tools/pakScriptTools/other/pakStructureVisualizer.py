from __future__ import annotations
import json
import os
import re
import sys
from typing import Dict, List
import xml.etree.ElementTree as ET

def getNameOfThing(thing: ET.Element) -> str:
	nameEl = thing.find("name")
	if nameEl is not None:
		name = nameEl.attrib["eng"] if "eng" in nameEl.attrib else nameEl.text
	else:
		name = "?"
	return name

class YaxActionsFile:
	id: str
	name: str
	actions: List[Dict[str, str]]	# { "id": str, "name": str }

	def __init__(self, id: str, name: str, actions: Dict[str, str]):
		self.id = id
		self.name = name
		self.actions = actions

	def toDictionary(self):
		return {
			"id": self.id,
			"name": self.name,
			"actions": self.actions
		}

class YaxGroup:
	id: str
	name: str
	childGroups: List[YaxGroup]
	actions: List[YaxActionsFile]

	def __init__(self, id: str, name: str, children: List[YaxGroup], actions: List[YaxActionsFile]):
		self.id = id
		self.name = name
		self.childGroups = children
		self.actions = actions

	def toDictionary(self):
		return {
			"id": self.id,
			"name": self.name,
			"childGroups": [child.toDictionary() for child in self.childGroups],
			"actions": [action.toDictionary() for action in self.actions]
		}

xml0 = sys.argv[1] if len(sys.argv) > 1 else "D:\\delete\\mods\\na\\blender\\extracted\\data012.cpk_unpacked\\st5\\nier2blender_extracted\\r501.dat\\pakExtracted\\r501_hap.pak\\0.xml"

groupsXml = ET.parse(xml0)

yaxGroups: List[YaxGroup] = []
idToGroupMap: Dict[str, YaxGroup] = {}

for group in groupsXml.findall("group"):
	id = group.find("id").text
	name = getNameOfThing(group)
	parent = idToGroupMap.get(group.find("parent").text)
	
	yaxGroup = YaxGroup(id, name, [], [])

	if parent is not None:
		parent.childGroups.append(yaxGroup)
	else:
		yaxGroups.append(yaxGroup)

	idToGroupMap[id] = yaxGroup

xml0Dir = os.path.dirname(xml0)

for file in os.listdir(xml0Dir):
	if not re.match(r"\d+\.xml", file):
		continue
	if file == "0.xml":
		continue

	actionsXml = ET.parse(os.path.join(xml0Dir, file)).getroot()
	yaxId = actionsXml.find("id").text
	yaxName = getNameOfThing(actionsXml)
	groupId = actionsXml.find("group").text

	yaxAction: YaxActionsFile = YaxActionsFile(yaxId, yaxName, [])
	idToGroupMap[groupId].actions.append(yaxAction)

	for action in actionsXml.findall("action"):
		id = action.find("id").text
		name = getNameOfThing(action)
		yaxAction.actions.append({ "id": id, "name": name })

structureFile = os.path.join(xml0Dir, "0_structure.json")
with open(structureFile, "w", encoding="utf-8") as f:
	structJson = json.dumps([group.toDictionary() for group in yaxGroups], indent=2, ensure_ascii=False)
	f.write(structJson)
	
print("Wrote structure to " + structureFile)

