from typing import List
import bpy
import xml.etree.ElementTree as ET

from mathutils import Vector

from ..util import makeCube, makeSphereObj, randomRgb, setCurrentCollection, strToFloat, tryAddCollection, xmlVecToVec3

def getNameOfThing(thing: ET.Element, prefix: str) -> str:
	nameEl = thing.find("name")
	if nameEl is not None:
		name = nameEl.attrib["eng"] if "eng" in nameEl.attrib else nameEl.text
		name = f"{prefix}-{name}"
	else:
		name = prefix
	return name

def importAreaCommand(action: ET.Element, color: List[float]):
	"""
	<area id="0xd7943d68">
		<size id="0xf7c0246a">1</size>
		<value id="0x1d775834">
			<code id="0x77153098">0x18cffd98</code>
			<position id="0x462ce4f5">274.931 -116.08 461.156</position>
			<rotation id="0x297c98f1">0 0 0</rotation>
			<scale id="0xec462584">13.318955 13.195042 16.192425</scale>
			<points id="0x27ba8e29">-1 -1 1 -1 1 1 -1 1</points>
			<height id="0xf54de50f">1</height>
		</value>
	</area>
		"""
	area = action.find("area")
	for i, areaObj in enumerate(area.findall("value")):
		loc = xmlVecToVec3(areaObj.find("position").text)
		rot = xmlVecToVec3(areaObj.find("rotation").text) if areaObj.find("rotation") is not None else (0, 0, 0)
		scale = xmlVecToVec3(areaObj.find("scale").text) if areaObj.find("scale") is not None else (1, 1, 1)
		cube = makeCube(f"{i}-Cube", None, color, False)
		cube.location = loc
		cube.rotation_euler = rot
		cube.scale = Vector(scale) * 2

def importEnemyGenerator(action: ET.Element, color: List[float]):
	"""
	<points id="0x27ba8e29">
		<attribute id="0xfa7aeffb">0x0</attribute>
		<nodes id="0x1d3d05fc">
			<size id="0xf7c0246a">1</size>
			<value id="0x1d775834">
				<point id="0xb7a5f324">325.75589 -113.48423 491.934448</point>
				<radius id="0x3b7c6e5a">5</radius>
				<rate id="0xdfec3f39">0</rate>
				<minDistance id="0xc95238e1">0</minDistance>
			</value>
		</nodes>
	</points>
	"""
	points = action.find("points")
	for i, point in enumerate(points.find("nodes").findall("value")):
		loc = xmlVecToVec3(point.find("point").text)
		radius = strToFloat(point.find("radius").text)
		sphere = makeSphereObj(f"{i}-Sphere", radius, None, color)
		sphere.location = loc


def importXml(root: ET.Element, prefix: str) -> None:
	yaxName = getNameOfThing(root, prefix)
	print(f"Importing {yaxName}")
	yaxRootColl = tryAddCollection("YAX", bpy.context.scene.collection)
	yaxColl = tryAddCollection(yaxName, yaxRootColl)
	setCurrentCollection(yaxColl)
	color = randomRgb(yaxName) + [0.5]

	actionsImported = False
	for action in root.findall("action"):
		actionCode = action.find("code").text
		if actionCode in ["0x58534a9e", "0x8cf2e32", "0x1571c131"]:
			# area command
			importAreaCommand(action, color)
			actionsImported = True
		elif actionCode == "0x6f0fb5bd":	# enemy generator
			importEnemyGenerator(action, color)
			actionsImported = True
		else:
			...
	
	if not actionsImported:
		bpy.data.collections.remove(yaxColl)
