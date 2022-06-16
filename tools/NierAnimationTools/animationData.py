from __future__ import annotations
import math
from typing import List, Set, Tuple
import bpy
from mathutils import Euler, Matrix, Vector
from .motUtils import boneGlobalLocationToLocal, boneGlobalRotationToLocal, getArmatureObject, getBoneCurrentValue, getBoneGlobalLocation, getLeftKeyframe, getRightKeyframe, interpolateLinearVal, interpolateSplineVal, rotateCoordinateToYUp, KeyFrame, rotateKeyframesToZUp
from .mot import MotRecord

class PropertyAnimation:
	_propertyNameToIndex = {
		"location": 0,
		"rotation_euler": 1,
		"scale": 2,
	}
	propertyName: str
	propertyNameIndex: int
	bone: bpy.types.PoseBone
	armatureObj: bpy.types.Object
	channelKeyFrames: Tuple[List[KeyFrame], List[KeyFrame], List[KeyFrame]]
	

	# def fromRecords(self, records: List[MotRecord], uniqueKeyframes: List[int]):
	def fromRecords(self, records: List[MotRecord]):
		self.propertyName = records[0].getPropertyPath()
		self.propertyNameIndex = PropertyAnimation._propertyNameToIndex[self.propertyName]
		self.bone = records[0].getBone()
		self.armatureObj = getArmatureObject()
		self.channelKeyFrames = [rec.interpolation.toKeyFrames() if rec else [] for rec in records]

		# fill missing channel with 1 default keyframe
		for i, keyframes in enumerate(self.channelKeyFrames):
			if not keyframes:
				defaultKeyframe = KeyFrame()
				defaultKeyframe.interpolationType = "CONSTANT"
				defaultKeyframe.frame = 0
				currentValue = getBoneCurrentValue(self.bone, self.propertyName, i)
				defaultKeyframe.value = rotateCoordinateToYUp(currentValue)[i]
				keyframes.append(defaultKeyframe)

		# ensure that at every keyframe all 3 channels are set
		uniqueKeyframes: Set[int] = set()
		for keyframes in self.channelKeyFrames:
			for keyframe in keyframes:
				uniqueKeyframes.add(keyframe.frame)
		uniqueKeyframes: List[int] = sorted(uniqueKeyframes)

		def repeatKeyframeAt(keyframes: List[KeyFrame], frame: int) -> KeyFrame:
			newKeyframe = KeyFrame()
			newKeyframe.interpolationType = keyframes[frame].interpolationType
			newKeyframe.frame = uniqueKeyframes[i]
			newKeyframe.value = keyframes[frame].value
			if newKeyframe.interpolationType == "BEZIER":
				newKeyframe.m0 = 0
				newKeyframe.m1 = 0
			return newKeyframe

		for keyframes in self.channelKeyFrames:
			processedKeyframes: List[KeyFrame] = []
			currentKeyframesQueue = keyframes[:]
			for i, uniqueKf in enumerate(uniqueKeyframes):
				# unique kf exists in channel
				if len(currentKeyframesQueue) > 0 and currentKeyframesQueue[0].frame == uniqueKf:
					processedKeyframes.append(currentKeyframesQueue.pop(0))
				# no more keyframes in channel but unique kf is missing, repeat last keyframe
				elif len(currentKeyframesQueue) == 0:
					newKeyframe = repeatKeyframeAt(keyframes, -1)
					keyframes.append(newKeyframe)
					processedKeyframes.append(newKeyframe)
				# unique kf is missing before any keyframes happened, repeat first keyframe
				elif len(processedKeyframes) == 0 and currentKeyframesQueue[0].frame > uniqueKf:
					newKeyframe = repeatKeyframeAt(keyframes, 0)
					keyframes.insert(0, newKeyframe)
					processedKeyframes.append(newKeyframe)
				# unique kf is missing between two keyframes, interpolate between them
				elif len(processedKeyframes) > 0 and currentKeyframesQueue[0].frame > uniqueKf:
					leftKf = processedKeyframes[-1]
					rightKf = currentKeyframesQueue[0]
					newKeyframe = KeyFrame()
					newKeyframe.interpolationType = leftKf.interpolationType
					newKeyframe.frame = uniqueKf
					if newKeyframe.interpolationType == "CONSTANT":
						newKeyframe.value = leftKf.value
					elif newKeyframe.interpolationType == "LINEAR":
						newKeyframe.value = interpolateLinearVal(leftKf, rightKf, uniqueKf)
					elif newKeyframe.interpolationType == "BEZIER":
						spline = interpolateSplineVal(leftKf, rightKf, uniqueKf)
						newKeyframe.value = spline.value
						newKeyframe.m0 = spline.m0
						newKeyframe.m1 = spline.m1
					else:
						raise Exception("Unknown interpolation type: " + newKeyframe.interpolationType)
					
					keyframes.insert(i, newKeyframe)
					processedKeyframes.append(newKeyframe)
				else:
					raise Exception("Unknown keyframe state")


			# for i, keyframe in enumerate(keyframes[:]):
			# 	if keyframe.frame in uniqueKeyframes:
			# 		continue
				
			# 	# interpolate between previous and next keyframe
			# 	newKeyframe = KeyFrame()
			# 	newKeyframe.interpolationType = keyframe.interpolationType
			# 	newKeyframe.frame = keyframe.frame
			# 	leftKF = getLeftKeyframe(keyframes, keyframe.frame) or keyframes[0]
			# 	if keyframe.interpolationType == "CONSTANT":
			# 		newKeyframe.value = leftKF.value
			# 	elif keyframe.interpolationType == "LINEAR":
			# 		rightKF = getRightKeyframe(keyframes, keyframe.frame)
			# 		newKeyframe.value = interpolateLinearVal(leftKF, rightKF, keyframe.frame)
			# 	elif keyframe.interpolationType == "BEZIER":
			# 		rightKF = getRightKeyframe(keyframes, keyframe.frame)
			# 		spline = interpolateSplineVal(leftKF, rightKF, keyframe.frame)
			# 		newKeyframe.value = spline.value
			# 		newKeyframe.m0 = spline.m0
			# 		newKeyframe.m1 = spline.m1

			# 	keyframes.insert(i, newKeyframe)
			# for i in range(len(keyframes), len(uniqueKeyframes)):
			# 	# repeat last keyframe
			# 	newKeyframe = KeyFrame()
			# 	newKeyframe.interpolationType = keyframes[-1].interpolationType
			# 	newKeyframe.frame = uniqueKeyframes[i]
			# 	newKeyframe.value = keyframes[-1].value
			# 	if newKeyframe.interpolationType == "BEZIER":
			# 		newKeyframe.m0 = 0
			# 		newKeyframe.m1 = 0
			# 	keyframes.append(newKeyframe)
		
		# check that all channels have the same number of keyframes
		maxKeyframes = max([len(keyframes) for keyframes in self.channelKeyFrames])
		for keyframes in self.channelKeyFrames:
			if len(keyframes) != maxKeyframes:
				raise Exception("Not all channels have the same number of keyframes")

		# rotate translation coordinates from y-up to blender's z-up coordinate system
		if self.propertyName == "location":
			rotateKeyframesToZUp(self.channelKeyFrames, True)
			# orig = self.channelKeyFrames[:]
			# self.channelKeyFrames[1] = orig[2]
			# self.channelKeyFrames[2] = orig[1]
			# for i in range(maxKeyframes):
			# 	self.channelKeyFrames[1][i].value *= -1
			# 	if self.channelKeyFrames[1][i].interpolationType == "BEZIER":
			# 		self.channelKeyFrames[1][i].m0 *= -1
			# 		self.channelKeyFrames[1][i].m1 *= -1
		elif self.propertyName == "rotation_euler":
			rotateKeyframesToZUp(self.channelKeyFrames, True)
			# for i in range(maxKeyframes):
				# self.channelKeyFrames[0][i].value -= math.pi / 2
				# self.channelKeyFrames[1][i].value -= math.pi / 2
				# self.channelKeyFrames[2][i].value += math.pi / 2
				# pass
		# 	orig = self.channelKeyFrames[:]
		# 	self.channelKeyFrames[0] = orig[2]
		# 	self.channelKeyFrames[2] = orig[0]
		# 	for i in range(maxKeyframes):
		# 		self.channelKeyFrames[0][i].value *= -1
		# 		self.channelKeyFrames[2][i].value *= -1
		# 		if self.channelKeyFrames[0][i].interpolationType == "BEZIER":
		# 			self.channelKeyFrames[0][i].m0 *= -1
		# 			self.channelKeyFrames[0][i].m1 *= -1
		# 		if self.channelKeyFrames[2][i].interpolationType == "BEZIER":
		# 			self.channelKeyFrames[2][i].m0 *= -1
		# 			self.channelKeyFrames[2][i].m1 *= -1
			
	def applyToBlender(self):
		# print("=================")
		# print(self.bone.name)
		# print(self.propertyName)

		if self.propertyName == "rotation_euler":
			self.bone.rotation_mode = "XYZ"
			prevRot = self.bone.rotation_euler.copy()

		boneProp = self.bone.path_resolve(self.propertyName)
		rig = getArmatureObject()
		for i in range(len(self.channelKeyFrames[0])):
			bpy.context.scene.frame_set(self.channelKeyFrames[0][i].frame)
			valueVec = Vector([self.channelKeyFrames[c][i].value for c in range(3)])

			if self.propertyName == "location":
				parentGlobalLoc = getBoneGlobalLocation(self.bone.parent, rig) if self.bone.parent else Vector((0, 0, 0))
				relToParentTarget = parentGlobalLoc + valueVec
				localLoc = boneGlobalLocationToLocal(self.bone, rig, relToParentTarget)
				for c in range(3):
					boneProp[c] = localLoc[c]
					self.bone.keyframe_insert(data_path=self.propertyName, index=c, frame=self.channelKeyFrames[0][i].frame)
					# TODO bezier handles
			elif self.propertyName == "rotation_euler":
				# initialLocation = self.bone.location.copy()
				# initialScale = self.bone.scale.copy()
				# self.bone.rotation_euler = (0, 0, 0)
				targetRotMat = Euler(valueVec).to_matrix()
				boneGlobal: Matrix = rig.matrix_world @ self.bone.matrix
				boneGlobalLoc, boneGlobalRot, boneGlobalScale = boneGlobal.decompose()
				boneGlobalRotMat = boneGlobalRot.to_euler("XYZ", prevRot).to_matrix()
				boneTargetGlobRotMat: Matrix = targetRotMat @ boneGlobalRotMat
				boneTargetGlobQuat = boneTargetGlobRotMat.to_quaternion()
				boneTargetGlobal =  Matrix.LocRotScale(boneGlobalLoc, boneTargetGlobQuat, boneGlobalScale)
				boneTargetMatrix = rig.matrix_world.inverted() @ boneTargetGlobal
				self.bone.matrix = boneTargetMatrix
				prevRot = self.bone.rotation_euler.copy()
				# self.bone.location = initialLocation
				# self.bone.scale = initialScale
				self.bone.keyframe_insert(data_path=self.propertyName, frame=self.channelKeyFrames[0][i].frame)
				# for c in range(3):
					# boneProp[c] = localRot[c]
					# self.bone.keyframe_insert(data_path=self.propertyName, index=c, frame=self.channelKeyFrames[0][i].frame)
					# TODO bezier handles
			else:
				for c in range(3):
					boneProp[c] = valueVec[c]
					self.bone.keyframe_insert(data_path=self.propertyName, index=c, frame=self.channelKeyFrames[0][i].frame)
					# TODO bezier handles

		# if self.propertyName == "location":
		# 	self.hasTranslationBeenAdjusted = True


