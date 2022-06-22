from typing import List
import bpy
import xml.etree.ElementTree as ET

from mathutils import Vector

from ..util import makeBezier, makeCube, makeSphereObj, randomRgb, setCurrentCollection, strToFloat, tryAddCollection, xmlVecToVec3

yaxColl: bpy.types.Collection

def getNameOfThing(thing: ET.Element, prefix: str) -> str:
	nameEl = thing.find("name")
	if nameEl is not None:
		name = nameEl.attrib["eng"] if "eng" in nameEl.attrib else nameEl.text
		name = f"{prefix}-{name}"
	else:
		name = prefix
	return name

def importArea(area: ET.Element, color: List[float]):
	for i, areaObj in enumerate(area.findall("value")):
		loc = xmlVecToVec3(areaObj.find("position").text)
		rot = xmlVecToVec3(areaObj.find("rotation").text) if areaObj.find("rotation") is not None else (0, 0, 0)
		scale = xmlVecToVec3(areaObj.find("scale").text) if areaObj.find("scale") is not None else (1, 1, 1)
		cube = makeCube(f"{i}-Cube", None, color, False)
		cube.location = loc
		cube.rotation_euler = rot
		cube.scale = Vector(scale) * 2

def importAreaCommand(action: ET.Element, color: List[float], prefix: str):
	setCurrentCollection(tryAddCollection(getNameOfThing(action, f"{prefix}-Action"), yaxColl))
	area = action.find("area")
	for i, areaObj in enumerate(area.findall("value")):
		loc = xmlVecToVec3(areaObj.find("position").text)
		rot = xmlVecToVec3(areaObj.find("rotation").text) if areaObj.find("rotation") is not None else (0, 0, 0)
		scale = xmlVecToVec3(areaObj.find("scale").text) if areaObj.find("scale") is not None else (1, 1, 1)
		cube = makeCube(f"{i}-Cube", None, color, False)
		cube.location = loc
		cube.rotation_euler = rot
		cube.scale = Vector(scale) * 2

def importEnemyGenerator(action: ET.Element, color: List[float], prefix: str):
	setCurrentCollection(tryAddCollection(getNameOfThing(action, f"{prefix}-Action"), yaxColl))
	points = action.find("points")
	for i, point in enumerate(points.find("nodes").findall("value")):
		loc = xmlVecToVec3(point.find("point").text)
		radius = strToFloat(point.find("radius").text)
		sphere = makeSphereObj(f"{i}-Sphere", radius, None, color)
		sphere.location = loc
	
	# if action.find("area") is not None:
	# 	importArea(action.find("area"), color)
	# if action.find("resetArea") is not None:
	# 	importArea(action.find("resetArea"), color)
	# if action.find("escapeArea") is not None:
	# 	importArea(action.find("escapeArea"), color)

def importEnemySet(action: ET.Element, color: List[float], prefix: str) -> None:
	setCurrentCollection(tryAddCollection(getNameOfThing(action, f"{prefix}-Action"), yaxColl))

	for i, layout in enumerate(action.find("layouts")):
		for j, enemy in enumerate(layout.find("layouts").findall("value")):
			emId = enemy.find("objID").text
			dummyCube = makeCube(f"{i}x{j}-{emId}", None, color)
			dummyCube.location = xmlVecToVec3(enemy.find("location").find("position").text)
			dummyCube.rotation_euler = xmlVecToVec3(enemy.find("location").find("rotation").text)
			dummyCube.scale = (1, 0.2, 2)
			# dummyCube.location[2] += 0.75

	# if action.find("area") is not None:
	# 	importArea(action.find("area"), color)
	# if action.find("resetArea") is not None:
	# 	importArea(action.find("resetArea"), color)
	# if action.find("escapeArea") is not None:
	# 	importArea(action.find("escapeArea"), color)

def importBezier(action: ET.Element, color: List[float], prefix: str) -> None:
	setCurrentCollection(tryAddCollection(getNameOfThing(action, f"{prefix}-Action"), yaxColl))

	curveData = action.find("curve")
	points = curveData.find("nodes").findall("value")
	points = [xmlVecToVec3(point.find("point").text) for point in points]
	
	handles = curveData.find("controls").findall("value")
	handles = [val.find("cp").text.split(" ") for val in handles]
	leftHandles = [xmlVecToVec3(" ".join(handle[:3])) for handle in handles]
	rightHandles = [xmlVecToVec3(" ".join(handle[3:])) for handle in handles]
	for i, invHandle in enumerate(leftHandles):
		vecToPoint = Vector(points[i]) - Vector(invHandle)
		leftHandles[i] = Vector(points[i]) + vecToPoint
	
	makeBezier(f"{prefix}-Bezier", points, leftHandles, rightHandles, None, color)

def importXml(root: ET.Element, prefix: str) -> None:
	global yaxColl

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
			importAreaCommand(action, color, prefix)
			actionsImported = True
		elif actionCode == "0x6f0fb5bd":	# enemy generator
			importEnemyGenerator(action, color, prefix)
			actionsImported = True
		elif actionCode == "0xe8fefe4b":	# enemy set
			importEnemySet(action, color, prefix)
			actionsImported = True
		elif actionCode == "0x5874fcd9":	# bezier
			importBezier(action, color, prefix)
			actionsImported = True
		else:
			...
	
	if not actionsImported:
		bpy.data.collections.remove(yaxColl)
