from typing import Dict, Set
from .animationData import PropertyAnimation
import bpy
from .mot import *
from .motUtils import *

def importMot(file: str) -> None:
	with open(file, "rb") as f:
		header = MotHeader()
		header.fromFile(f)

		# new animation action
		if header.animationName in bpy.data.actions:
			bpy.data.actions.remove(bpy.data.actions[header.animationName])
		action = bpy.data.actions.new(header.animationName)
		armatureObj = getArmatureObject()
		if not armatureObj.animation_data:
			armatureObj.animation_data_create()
		armatureObj.animation_data.action = action
		
		# clear pose data
		for bone in armatureObj.pose.bones:
			bone.location = (0, 0, 0)
			bone.rotation_quaternion = (1, 0, 0, 0)
			bone.rotation_euler = (0, 0, 0)
			bone.scale = (1, 1, 1)

		# import
		f.seek(header.recordsOffset)
		records = []
		for i in range(header.recordsCount):
			record = MotRecord()
			record.fromFile(f)
			records.append(record)
		
		# create keyframes
		channelGroups: Dict[str, List[MotRecord]] = {}
		record: MotRecord
		for record in records:
			if not record.getBone():
				continue
			key = f"{record.getBone().name}:{record.getPropertyPath()}"
			if key not in channelGroups:
				channelGroups[key] = [None, None, None]
			
			channelGroups[key][record.getPropertyIndex()] = record

		# uniqueKeyframes: Set[int] = set()
		# for record in records:
		# 	for keyframe in record.interpolation.getKeyframeIndices():
		# 		uniqueKeyframes.add(keyframe)
		# uniqueKeyframes: List[int] = sorted(uniqueKeyframes)

		animations: List[PropertyAnimation] = []
		for group in channelGroups.values():
			animation = PropertyAnimation()
			animation.fromRecords(group)
			# animation.fromRecords(group, uniqueKeyframes)
			animations.append(animation)
		
		# sort by hierarchy, since translation is relative to parent
		animations.sort(key=lambda a: f"{len(a.bone.parent_recursive)}:{int(a.bone.name[4:])}")
		
		# apply to blender
		for animation in animations:
			animation.applyToBlender()

