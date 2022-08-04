from __future__ import annotations
from io import BufferedReader
import struct
import sys
from typing import Dict, List
import xml.dom.minidom
from xml.etree.ElementTree import Element, SubElement, tostring as xmlToString
from other.japToEngTranslation import japToEng
from other.hashToStringMap import hashToStringMap

# Utils

def read_uint8(file) -> int:
	entry = file.read(1)
	return struct.unpack('<B', entry)[0]

def read_uint32(file) -> int:
	entry = file.read(4)
	return struct.unpack('<I', entry)[0]

def read_string(file: BufferedReader, pos) -> str:
	initialPos = file.tell()
	file.seek(pos)
	binaryString = b""
	while True:
		char = file.read(1)
		if char == b'\x00':
			break
		binaryString += char
	file.seek(initialPos)
	return binaryString.decode('shift-jis')

def lookupElementHash(element: Element):
	try:
		hashVal = int(element.text, 16)
		if hashVal != 0 and hashVal in hashToStringMap:
			element.attrib["str"] = hashToStringMap[hashVal]
	except:
		pass

def isAscii(s: str) -> bool:
	try:
		s.encode("ascii")
		return True
	except UnicodeEncodeError:
		return False

# Data structures

class XmlNode:
	indentation: int
	tag: str
	tagId: int
	value: str
	translatedValue: str

	children: List[XmlNode]

	def __init__(self, file: BufferedReader = None):
		self.indentation = -1
		self.tag = ""
		self.tagId = 0
		self.value = ""
		self.translatedValue = ""
		self.children = []
		if not file:
			return
		self.indentation = read_uint8(file)
		tagId = read_uint32(file)
		self.tag = hashToStringMap.get(tagId, "UNKNOWN")
		self.tagId = tagId
		valueOffset = read_uint32(file)
		if valueOffset != 0:
			self.value = read_string(file, valueOffset)
			if not isAscii(self.value):
				self.translatedValue = japToEng(self.value)

	def __str__(self):
		return f"{'    ' * self.indentation}{self.tag}: {self.value}"
	
	def toXml(self) -> Element:
		element = Element(self.tag)
		if self.tag == "UNKNOWN":
			element.set("id", hex(self.tagId))
		element.text = self.value
		if self.value.startswith("0x") and len(self.value) > 2:
			lookupElementHash(element)
		if self.translatedValue:
			element.set("eng", self.translatedValue)
		for child in self.children:
			element.append(child.toXml())
		return element

# Main

def yaxToXml(yaxFile: str, outFile: str|None = None):
	with open(yaxFile, "rb") as f:
		nodeCount = read_uint32(f)
		
		# read flat tree
		nodes: List[XmlNode] = []
		for i in range(nodeCount):
			nodes.append(XmlNode(f))
		
		# assemble tree from indents
		rootNode = XmlNode()
		rootNode.tag = "root"
		for node in nodes:
			if node.indentation == 0:
				rootNode.children.append(node)
				continue
			targetIndent = node.indentation - 1
			parent = rootNode.children[-1]
			while parent.indentation != targetIndent:
				parent = parent.children[-1]
			parent.children.append(node)

		# write xml
		rootXml = rootNode.toXml()
		rawXmlStr = xmlToString(rootXml, encoding="utf-8")
		if type(rawXmlStr) == bytes:
			xmlStr = rawXmlStr.decode("utf-8")
		dom = xml.dom.minidom.parseString(xmlStr)
		xmlStr = dom.toprettyxml(indent="\t", encoding="utf-8")
		
		xmlName = outFile or yaxFile.replace(".yax", ".xml") if ".yax" in yaxFile else yaxFile + ".xml"
		with open(xmlName, "wb") as f:
			f.write(xmlStr)

if __name__ == "__main__":
	yaxFiles = sys.argv[1:]
	for yaxFile in yaxFiles:
		if not "yax" in yaxFile:
			if len(yaxFiles) > 1:
				#To allow manually processing singular non *.yax files
				print(yaxFile , " is not a *.yax file. Skipping...")
				continue
		
		yaxToXml(yaxFile)
		print(f"Converted {yaxFile} to xml")
