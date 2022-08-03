from math import radians
from typing import Dict, List
import bpy
from mathutils import Euler, Matrix, Vector

class KeyFrame:
	interpolationType: str
	frame: int
	value: float
	m0: float
	m1: float

class Spline:
	frame: int
	value: float
	m0: float
	m1: float

def getArmatureObject() -> bpy.types.Object:
	for obj in bpy.data.objects:
		if obj.type == "ARMATURE":
			return obj
	return None

def getFCurve(armatureObj: bpy.types.Object, bone: bpy.types.PoseBone, property: str, index: int) -> bpy.types.FCurve:
	for fcurve in armatureObj.animation_data.action.fcurves:
		if fcurve.data_path == f"pose.bones[\"{bone.name}\"].{property}" and fcurve.array_index == index:
			return fcurve
	return None

def rotateKeyframesToZUp(vecYUp: List[List[KeyFrame]], invertY: bool) -> None:
	orig = vecYUp[:]
	vecYUp[1] = orig[2]
	vecYUp[2] = orig[1]
	if invertY:
		for i in range(len(vecYUp[1])):
			vecYUp[1][i].value *= -1
			if vecYUp[1][i].interpolationType == "BEZIER":
				vecYUp[1][i].m0 *= -1
				vecYUp[1][i].m1 *= -1

def rotateCoordinateToYUp(vecZUp: Vector, invertY: bool) -> Vector:
	if invertY:
		return Vector((vecZUp[0], vecZUp[2], -vecZUp[1]))
	else:
		return Vector((vecZUp[0], vecZUp[2], vecZUp[1]))
	
def getBoneCurrentValue(bone: bpy.types.PoseBone, property: str) -> Vector:
	if property == "location":
		parentLoc = bone.parent.head if bone.parent else Vector(0, 0, 0)
		ownLoc = bone.head
		locRelToParent = ownLoc - parentLoc
		return locRelToParent
	elif property == "rotation_euler":
		return bone.rotation_euler
	elif property == "scale":
		return bone.scale
	else:
		raise Exception(f"Unknown property: {property}")

def getLeftKeyframe(keyframes: List[KeyFrame], frame: int) -> KeyFrame:
	for i, keyframe in enumerate(keyframes):
		if keyframe.frame == frame:
			return keyframe
		elif keyframe.frame > frame:
			if i == 0:
				return keyframe
			else:
				return keyframes[i - 1]

def getRightKeyframe(keyframes: List[KeyFrame], frame: int) -> KeyFrame:
	for i, keyframe in enumerate(keyframes):
		if keyframe.frame == frame:
			return keyframe
		elif keyframe.frame < frame:
			if i == len(keyframes) - 1:
				return keyframe
			else:
				return keyframes[i + 1]

def interpolateLinearVal(p0: KeyFrame, p1: KeyFrame, frame: int) -> float:
	return \
		(1 - (frame - p0.frame) / (p1.frame - p0.frame)) * p0.value + \
		(frame - p0.frame) / (p1.frame - p0.frame) * p1.value

def interpolateSplineVal(p0: KeyFrame, p1: KeyFrame, frame: int) -> Spline:
	# float t = (float)(index - keys[i].index)/(keys[i+1].index - keys[i].index)
	# float val = (2*t^3 - 3*t^2 + 1)*p0 + (t^3 - 2*t^2 + t)*m0 + (-2*t^3 + 3*t^2)*p1 + (t^3 - t^2)*m1;
	
	t = (frame - p0.frame) / (p1.frame - p0.frame)
	val = (2 * t ** 3 - 3 * t ** 2 + 1) * p0.value + (t ** 3 - 2 * t ** 2 + t) * p0.m1 + (-2 * t ** 3 + 3 * t ** 2) * p1.value + (t ** 3 - t ** 2) * p1.m1
	spline = Spline()
	spline.frame = frame
	spline.value = val
	spline.m0 = p0.m1 * (1 - t) + p1.m0 * t
	spline.m1 = spline.m0
	return spline

def getBoneGlobalLocation(bone: bpy.types.PoseBone, armatureObj: bpy.types.Object) -> Vector:
	return (armatureObj.matrix_world @ bone.matrix).to_translation()

def boneGlobalLocationToLocal(bone: bpy.types.PoseBone, armatureObj: bpy.types.Object, globLoc: Vector) -> Vector:
	return armatureObj.convert_space(
		pose_bone=bone,
		matrix=Matrix.Translation(globLoc),
		from_space="WORLD",
		to_space="LOCAL"
	).to_translation()

def getBoneGlobalRotation(bone: bpy.types.PoseBone, armatureObj: bpy.types.Object) -> Vector:
	return (armatureObj.matrix_world @ bone.matrix).to_euler()

def boneGlobalRotationToLocal(bone: bpy.types.PoseBone, armatureObj: bpy.types.Object, globRot: Vector) -> Vector:
	return Vector(armatureObj.convert_space(
		pose_bone=bone,
		matrix=Euler(globRot).to_matrix().to_4x4(),
		from_space="WORLD",
		to_space="LOCAL"
	).to_euler())

def makeBoneRotOffsetMap(armatureObj: bpy.types.Object) -> Dict[bpy.types.PoseBone, Vector]:
	map = {}
	for bone in armatureObj.pose.bones:
		map[bone] = boneGlobalRotationToLocal(bone, armatureObj, (radians(90), 0, 0)) * -1
	return map
