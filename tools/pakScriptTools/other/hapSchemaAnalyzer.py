from __future__ import annotations
from enum import Enum
import json
import os
import re
import sys
from typing import Any, Dict, List
import xml.etree.ElementTree as ET
from xml.dom import minidom
import zlib
from hashToStringMap import hashToStringMap
import random

searchDir = "D:\\delete\\mods\\na\\blender\\extracted\\"

def crc32(text: str) -> int:
	return zlib.crc32(text.encode('ascii', 'ignore')) & 0xffffffff

def randomStr(len: int = 16) -> str:
	return ''.join(random.choice("0123456789acbcdefghijklmnopqrstuvwxyz") for i in range(len))

def isInt(s: str) -> bool:
	try:
		int(s)
		return True
	except ValueError:
		return False

def isHexInt(s: str) -> bool:
	try:
		int(s, 16)
		return True
	except ValueError:
		return False

def isHashed(val: int) -> bool:
	return val != 0 and val in hashToStringMap

def isFloat(s: str) -> bool:
	try:
		float(s)
		return True
	except ValueError:
		return False

def isVector(s: str) -> bool:
	vals = s.split(" ")
	return all(isFloat(x) for x in vals)

class BoolState(Enum):
	Unknown = 0
	Always = 1
	Never = 2
	Sometimes = 3

class XmlDataType:
	type: str
	usages: int
	fileUsages: Dict[str, int] # [parentId, count]

	def __init__(self, type: str):
		self.type = type
		self.usages = 1
		self.fileUsages = {}
	
	def newFileUsage(self, parentId: str) -> None:
		if parentId not in self.fileUsages:
			self.fileUsages[parentId] = 0
		self.fileUsages[parentId] += 1

	def updateWith(self, other: str, parentId: str) -> XmlDataType:
		raise NotImplementedError()

	def toDict(self, suffix: Any) -> Dict[str, Any]:
		raise NotImplementedError()

	@classmethod
	def fromString(cls, s: str, parentId: str) -> XmlDataType:
		if isInt(s):
			return XmlDataTyeInt().updateWith(s, parentId)
		elif isHexInt(s):
			return XmlDataTypeHex().updateWith(s, parentId)
		elif isFloat(s):
			return XmlDataTypeFloat().updateWith(s, parentId)
		elif isVector(s):
			return XmlDataTypeVector().updateWith(s, parentId)
		else:
			return XmlDataTypeString().updateWith(s, parentId)

class XmlDataTypeMinMax(XmlDataType):
	min: int
	max: int

	def initMinMax(self):
		self.min = sys.maxsize
		self.max = -sys.maxsize
	
	def updateMinMax(self, val: int):
		self.min = min(self.min, val)
		self.max = max(self.max, val)

class XmlDataTyeInt(XmlDataTypeMinMax):

	def __init__(self):
		super().__init__("int")
		self.initMinMax()

	def updateWith(self, other: str, parentId: str) -> XmlDataType:
		if isInt(other):
			self.usages += 1
			self.newFileUsage(parentId)
			val = int(other)
			self.updateMinMax(val)
			return self
		elif isHexInt(other):
			return XmlDataTypeHex().updateWith(other, parentId)
		elif isFloat(other):
			return XmlDataTypeFloat().updateWith(other, parentId)
		else:
			return XmlDataTypeString().updateWith(other, parentId)
	
	def toDict(self, suffix: Any) -> Dict[str, Any]:
		d = { f"type{suffix}": self.type }
		if self.min != self.max:
			d[f"min{suffix}"] = str(self.min)
			d[f"max{suffix}"] = str(self.max)
		else:
			d[f"value{suffix}"] = str(self.min)
		return d


class XmlDataTypeHex(XmlDataTypeMinMax):
	isHashed: BoolState

	def __init__(self):
		super().__init__("hex")
		self.isHashed = BoolState.Unknown
		self.initMinMax()

	def updateWith(self, other: str, parentId: str) -> XmlDataType:
		if isInt(other):
			return XmlDataTyeInt().updateWith(other, parentId)
		elif isHexInt(other):
			self.usages += 1
			self.newFileUsage(parentId)
			val = int(other, 16)
			self.updateMinMax(val)
			if isHashed(val):
				if self.isHashed == BoolState.Never and val != 0:
					self.isHashed = BoolState.Sometimes
				elif self.isHashed == BoolState.Unknown:
					self.isHashed = BoolState.Always
			else:
				if self.isHashed == BoolState.Always and val != 0:
					self.isHashed = BoolState.Sometimes
				elif self.isHashed == BoolState.Unknown:
					self.isHashed = BoolState.Never
			return self
		elif isFloat(other):
			return XmlDataTypeFloat().updateWith(other, parentId)
		else:
			return XmlDataTypeString().updateWith(other, parentId)
		
	def toDict(self, suffix: Any) -> Dict[str, Any]:
		d = { f"type{suffix}": self.type }
		if self.min != self.max:
			d[f"min{suffix}"] = f"0x{self.min:08x}"
			d[f"max{suffix}"] = f"0x{self.max:08x}"
		else:
			d[f"value{suffix}"] = f"0x{self.min:08x}"
		if self.isHashed == BoolState.Always:
			d[f"hashed{suffix}"] = "true"
		elif self.isHashed == BoolState.Never:
			d[f"hashed{suffix}"] = "false"
		elif self.isHashed == BoolState.Sometimes:
			d[f"hashed{suffix}"] = "sometimes"
		return d

class XmlDataTypeFloat(XmlDataTypeMinMax):
	type = "float"
	min: float
	max: float

	def __init__(self):
		super().__init__("float")
		self.initMinMax()
	
	def updateWith(self, other: str, parentId: str) -> XmlDataType:
		if isFloat(other):
			self.usages += 1
			self.newFileUsage(parentId)
			val = float(other)
			self.updateMinMax(val)
			return self
		elif isInt(other):
			return XmlDataTyeInt().updateWith(other, parentId)
		elif isHexInt(other):
			return XmlDataTypeHex().updateWith(other, parentId)
		else:
			return XmlDataTypeString().updateWith(other, parentId)
	
	def toDict(self, suffix: Any) -> Dict[str, Any]:
		d = { f"type{suffix}": self.type }
		if self.min != self.max:
			d[f"min{suffix}"] = f"{self.min:.2f}"
			d[f"max{suffix}"] = f"{self.max:.2f}"
		else:
			d[f"value{suffix}"] = f"{self.min:.2f}"
		return d

class XmlDataTypeString(XmlDataType):
	def __init__(self):
		super().__init__("string")
	
	def updateWith(self, other: str, parentId: str) -> XmlDataType:
		self.usages += 1
		self.newFileUsage(parentId)
		return self
	
	def toDict(self, suffix: Any) -> Dict[str, Any]:
		d = { f"type{suffix}": self.type }
		return d

class XmlDataTypeVector(XmlDataTypeMinMax):
	def __init__(self):
		super().__init__("vector")
		self.type = "vector"
		self.initMinMax()
	
	def updateWith(self, other: str, parentId: str) -> XmlDataType:
		if isVector(other):
			self.usages += 1
			self.newFileUsage(parentId)
			count = len(other.split(" "))
			self.updateMinMax(count)
			return self
		elif isInt(other):
			return XmlDataTyeInt().updateWith(other, parentId)
		elif isHexInt(other):
			return XmlDataTypeHex().updateWith(other, parentId)
		elif isFloat(other):
			return XmlDataTypeFloat().updateWith(other, parentId)
		else:
			return XmlDataTypeString().updateWith(other, parentId)

	def toDict(self, suffix: Any) -> Dict[str, Any]:
		d = { f"type{suffix}": self.type }
		if self.min != self.max:
			d[f"min_items{suffix}"] = str(self.min)
			d[f"max_items{suffix}"] = str(self.max)
		else:
			d[f"items{suffix}"] = str(self.min)
		return d

class XmlInfo:
	tagName: str
	dataTypes: List[XmlDataType]
	curTypeIndex: int
	usages: int
	fileUsages: Dict[str, int] # [parentId, count]
	children: List[XmlInfo]
	childTags: Dict[str, Any]
	# maxRepeats: int

	def __init__(self, tagName: str):
		self.tagName = tagName
		self.dataTypes = []
		self.curTypeIndex = 0
		self.usages = 0
		self.fileUsages = {}
		self.children = []
		self.childTags = {}
		# self.maxRepeats = 0
	
	def updateWith(self, other: ET.Element, parentId: str) -> XmlInfo:
		self.usages += 1
		if parentId not in self.fileUsages:
			self.fileUsages[parentId] = 0
		self.fileUsages[parentId] += 1
		childrenParentId = randomStr(16)
		# self.maxRepeats = max(self.maxRepeats, len(other))
		
		textVal = other.text.strip() if other.text else ""
		if len(self.dataTypes) == 0:
			if len(textVal) > 0:
				self.dataTypes.append(XmlDataType.fromString(textVal, childrenParentId))
		else:
			if len(textVal) > 0:
				lastType = self.dataTypes[self.curTypeIndex]
				newType = lastType.updateWith(textVal, childrenParentId)
				if newType != lastType:
					for i, existingType in enumerate(self.dataTypes):
						if type(existingType) == type(newType):
							existingType.updateWith(textVal, childrenParentId)
							self.curTypeIndex = i
							break
					else:
						self.dataTypes.append(newType)
						self.curTypeIndex = len(self.dataTypes) - 1
		
		i = 0 if len(self.children) > 0 else -1
		for child in other:
			# actions get special treatment
			if child.tag == "action":
				# try find existing action info
				actionCode = int(child.find("code").text, 16)
				for existingChild in self.children:
					if isinstance(existingChild, XmlActionInfo) and existingChild.actionCode == actionCode:
						existingChild.updateWith(child, childrenParentId)
						break
				else:
					# create new action info
					self.children.append(XmlActionInfo(child).updateWith(child, childrenParentId))
				i += 1
				continue

			# find child with same tag
			if child.tag in self.childTags:
				for existingChild in self.children[i:]:
					if existingChild.tagName == child.tag:
						existingChild.updateWith(child, childrenParentId)
						break
					i += 1
				else:
					# search from beginning
					# print("search from beginning")
					tmpI = 0
					for existingChild in self.children:
						if existingChild.tagName == child.tag:
							existingChild.updateWith(child, childrenParentId)
							break
						tmpI += 1
						i = max(i, tmpI)
					else:
						raise Exception(f"Could not find child with tag {child.tag}")
			else:
				i += 1
				self.children.insert(i, XmlInfo(child.tag).updateWith(child, childrenParentId))
				self.childTags[child.tag] = None

			# # append at end
			# if i >= len(self.children):
			# 	self.children.append(XmlInfo.fromXml(child).updateWith(child, childrenParentId))
			# 	i = len(self.children)
			# 	continue
			
			# # find update position
			# updateI = i
			# while updateI < len(self.children) and not isSameTagGroup(self.children[updateI], child):
			# 	updateI += 1
			# if updateI < len(self.children) and isSameTagGroup(self.children[updateI], child):
			# 	i = updateI
			# 	self.children[i].updateWith(child, childrenParentId)
			# else:
			# 	# insert
			# 	self.children.insert(i, XmlInfo.fromXml(child))
			# 	self.children[i].updateWith(child, childrenParentId)
			# # i += 1

		return self
	
	def toXml(self) -> ET.Element:
		element = ET.Element(self.tagName)
		for i, dataType in enumerate(self.dataTypes):
			suffix = "" if len(self.dataTypes) == 1 else f"_{i}"
			dataTypeDict = dataType.toDict(suffix)
			typeUsages = len(dataType.fileUsages)
			if typeUsages < self.usages:
				probability = typeUsages / self.usages
				if probability > 1:
					print(f"Warning: {probability} > 1")
				dataTypeDict[f"usage{suffix}"] = f"{probability:.1%}"
			# join attrib dicts
			for key, value in dataTypeDict.items():
				element.attrib[key] = value
		for child in self.children:
			childXml = child.toXml()
			childUsages = len(child.fileUsages)
			if childUsages < self.usages:
				probability = childUsages / self.usages
				if probability > 1:
					print(f"Warning: {probability} > 1")
				# probability = min(1, childUsages / self.usages)
				optional = ET.Element("optional")
				optional.attrib["probability"] = f"{probability:.1%}"
				optional.append(childXml)
				element.append(optional)
			else:
				element.append(childXml)
		return element
	
	@classmethod
	def fromXml(cls, xml: ET.Element) -> XmlInfo:
		if xml.tag == "action":
			return XmlActionInfo(xml)
		else:
			return XmlInfo(xml.tag)
			

class XmlActionInfo(XmlInfo):
	actionCode: int

	def __init__(self, element: ET.Element):
		super().__init__(element.tag)
		self.actionCode = int(element.find("code").text, 16)

	def toXml(self) -> ET.Element:
		element = super().toXml()
		element.set("type", hashToStringMap[self.actionCode])
		return element

def isSameTagGroup(info: XmlInfo, element: ET.Element) -> bool:
	if info.tagName != element.tag:
		return False
	if info.tagName == "action":
		return info.actionCode == int(element.find("code").text, 16)
	return True
	
rootInfo = XmlInfo.fromXml(ET.Element("root"))
def analyzeScheme(file: str):
	xml = ET.parse(file)
	root = xml.getroot()
	
	rootInfo.updateWith(root, randomStr(8))

for root, dirs, files in os.walk(searchDir):
	for file in files:
		if not file.endswith(".yax"):
			continue
		file = file.replace(".yax", ".xml")
		# if file == "0.xml":
		# 	continue
		if not os.path.exists(os.path.join(root, file)):
			continue
		# if "corehap" in root:
		# 	continue
		analyzeScheme(os.path.join(root, file))

rootXmlSchema = rootInfo.toXml()
xmlStr = ET.tostring(rootXmlSchema, encoding="unicode")
prettyStr = minidom.parseString(xmlStr).toprettyxml(indent="\t")
with open("schema.xml", "w") as f:
	f.write(prettyStr)
