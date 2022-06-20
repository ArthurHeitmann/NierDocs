from __future__ import annotations
from io import BufferedReader, BufferedWriter
import struct
import sys
from typing import Dict, List, Set
from xml.etree.ElementTree import XMLParser, fromstring as xmlFromString, Element

def writeString(string: str, file: BufferedWriter):
	file.write(string.encode('shift-jis'))
	file.write(b'\x00')

def writeUint8(value: int, file: BufferedWriter):
	file.write(struct.pack('<B', value))

def writeUint32(value: int, file: BufferedWriter):
	file.write(struct.pack('<I', value))

class XmlNode:
	indentation: int
	tagId: int
	valueOffset: int

	value: str

	def __init__(self, indentation: int, tagId: int, value: str):
		self.indentation = indentation
		self.tagId = tagId
		self.value = value
	
	def writeToFile(self, file: BufferedWriter):
		writeUint8(self.indentation, file)
		writeUint32(self.tagId, file)
		writeUint32(self.valueOffset, file)


def xmlToYax(xmlFile: str):
	with open(xmlFile, "r", encoding="utf-8") as file:
		xmlBytes = file.read()
		xmlFileContents = xmlBytes
	xmlRoot = xmlFromString(xmlFileContents)

	stringSet: List[str] = []
	stringOffsets: Dict[str, int] = {}
	lastOffset = 0
	def putStringGetOffset(string: str) -> int:
		global lastOffset
		if not string:
			return 0
		if string in stringSet:
			return stringOffsets[string]

		stringSet.append(string)
		stringOffsets[string] = lastOffset
		retOff = lastOffset
		strByteLength = len(string.encode('shift-jis')) + 1
		lastOffset += strByteLength
		return retOff

	# read flat tree, create nodes
	nodes: List[XmlNode] = []
	def addNodeToList(node: Element, indentation: int):
		tagId = int(node.get("id"), 16)
		nodeText = node.text.strip()
		nodes.append(XmlNode(indentation, tagId, nodeText))
		for child in node:
			addNodeToList(child, indentation + 1)
	for child in xmlRoot:
		addNodeToList(child, 0)

	# make string set
	lastOffset = 4 + len(nodes) * 9
	for node in nodes:
		node.valueOffset = putStringGetOffset(node.value)

	outFileName = xmlFile.replace(".xml", ".yax") if ".xml" in xmlFile else xmlFile + ".yax"
	with open(outFileName, "wb") as f:
		# node length
		writeUint32(len(nodes), f)
		# nodes
		for node in nodes:
			node.writeToFile(f)
		# strings
		for string in stringSet:
			writeString(string, f)

if __name__ == "__main__":
	xmlFiles = sys.argv[1:]

	for xmlFile in xmlFiles:
		xmlToYax(xmlFile)
		print(f"Converted {xmlFile} to yax")
