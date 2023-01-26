from __future__ import annotations
from typing import List
import bpy
from .motUtils import *
from .ioUtils import *
from io import BufferedReader

class MotHeader:
	id: str
	hash: int
	flag: int
	frameCount: int
	recordsOffset: int
	recordsCount: int
	unknown: int
	animationName: str

	def fromFile(self, file: BufferedReader):
		self.id = read_string(file, 4)
		self.hash = read_uint32(file)
		self.flag = read_uint16(file)
		self.frameCount = read_int16(file)
		self.recordsOffset = read_uint32(file)
		self.recordsCount = read_uint32(file)
		self.unknown = read_uint32(file)
		self.animationName = read_string(file)

class MotRecord:
	boneIndex: int
	propertyIndex: int
	flag: int
	interpolationsCount: int
	count: int
	value: float
	interpolationsOffset: int
	interpolation: MotInterpolation

	def fromFile(self, file: BufferedReader):
		self.boneIndex = read_int16(file)
		self.propertyIndex = read_int8(file)
		self.flag = read_int8(file)
		self.interpolationsCount = read_int16(file)
		self.count = read_uint16(file)

		pos = file.tell()
		self.value = read_float(file)
		file.seek(pos)
		self.interpolationsOffset = read_uint32(file)

		self.interpolation = MotInterpolation.fromRecordAndFile(self, file)
	
	def getBone(self) -> bpy.types.PoseBone|None:
		rig = getArmatureObject()
		boneName: str = ""
		if self.boneIndex == -1:
			return None
		else:
			for bone in rig.data.bones:
				if bone["ID"] == self.boneIndex:
					boneName = bone.name
					break
		if not boneName:
			return None
		return rig.pose.bones.get(boneName)
	
	def getPropertyPath(self) -> str:
		if self.propertyIndex in {0, 1, 2}:
			return "location"
		elif self.propertyIndex in {3, 4, 5}:
			return "rotation_euler"
		elif self.propertyIndex in {7, 8, 9}:
			return "scale"
		else:
			raise Exception(f"Unknown property index: {self.propertyIndex}")
	
	def getPropertyIndex(self) -> int:
		if self.propertyIndex in {0, 3, 7}:
			return 0
		elif self.propertyIndex in {1, 4, 8}:
			return 1
		elif self.propertyIndex in {2, 5, 9}:
			return 2
		else:
			raise Exception(f"Unknown property index: {self.propertyIndex}")

class MotInterpolation:
	record: MotRecord
	
	def fromFile(self, file: BufferedReader):
		raise NotImplementedError()

	def toKeyFrames(self) -> List[KeyFrame]:
		raise NotImplementedError()
	
	def getKeyframeIndices(self) -> List[int]:
		raise NotImplementedError()
	
	@staticmethod
	def applyInterpolationToKeyFrame(prev: KeyFrameCombo|None, cur: KeyFrameCombo):
		raise NotImplementedError()

	@classmethod
	def fromRecordAndFile(self, record: MotRecord, file: BufferedReader) -> MotInterpolation:
		interpolation: MotInterpolation

		if record.flag == 0 or record.flag == -1:
			interpolation = MotInterpolConst()
		elif record.flag == 1:
			interpolation = MotInterpolValues()
		elif record.flag == 2:
			interpolation = MotInterpol2()
		elif record.flag == 3:
			interpolation = MotInterpol3()
		elif record.flag == 4:
			interpolation = MotInterpolSplines()
		elif record.flag == 5:
			interpolation = MotInterpol5()
		elif record.flag == 6:
			interpolation = MotInterpol6()
		elif record.flag == 7:
			interpolation = MotInterpol7()
		elif record.flag == 8:
			interpolation = MotInterpol8()
		else:
			raise Exception(f"Unknown interpolation flag: {record.flag}")
		
		interpolation.record = record
		interpolation.fromFile(file)

		return interpolation

class MotInterpolConst(MotInterpolation):
	value: float

	def fromFile(self, file: BufferedReader):
		self.value = self.record.value
	
	def toKeyFrames(self) -> List[KeyFrame]:
		keyframe = KeyFrame()
		keyframe.interpolationType = "CONSTANT"
		keyframe.frame = 0
		keyframe.value = self.value
		keyframe.applyInterpolation = MotInterpolConst.applyInterpolationToKeyFrame
		return [keyframe]
	
	def getKeyframeIndices(self) -> List[int]:
		return [0]
	
	@staticmethod
	def applyInterpolationToKeyFrame(prev: KeyFrameCombo|None, cur: KeyFrameCombo):
		cur.blend.interpolation = "CONSTANT"

class MotInterpolValues(MotInterpolation):
	values: List[float]

	def fromFile(self, file: BufferedReader):
		pos = file.tell()
		file.seek(pos + self.record.interpolationsOffset - 12)

		self.values = []
		for _ in range(self.record.interpolationsCount):
			self.values.append(read_float(file))
		
		file.seek(pos)
		
	def toKeyFrames(self) -> List[KeyFrame]:
		keyframes = []
		for i, value in enumerate(self.values):
			keyframe = KeyFrame()
			keyframe.interpolationType = "LINEAR"
			keyframe.frame = i
			keyframe.value = value
			keyframes.append(keyframe)
			keyframe.applyInterpolation = MotInterpolValues.applyInterpolationToKeyFrame
		return keyframes
	
	def getKeyframeIndices(self) -> List[int]:
		return list(range(len(self.values)))
	
	@staticmethod
	def applyInterpolationToKeyFrame(prev: KeyFrameCombo|None, cur: KeyFrameCombo):
		cur.blend.interpolation = "LINEAR"
		
class MotInterpol2(MotInterpolValues):
	def fromFile(self, file: BufferedReader):
		pos = file.tell()
		file.seek(pos + self.record.interpolationsOffset - 12)

		p = read_float(file)
		dp = read_float(file)
		self.values = []
		for _ in range(self.record.interpolationsCount):
			self.values.append(p + dp * read_uint16(file))

		file.seek(pos)
		
class MotInterpol3(MotInterpolValues):
	def fromFile(self, file: BufferedReader):
		pos = file.tell()
		file.seek(pos + self.record.interpolationsOffset - 12)

		p = read_PgHalf(file)
		dp = read_PgHalf(file)
		self.values = []
		for _ in range(self.record.interpolationsCount):
			self.values.append(p + dp * read_uint8(file))

		file.seek(pos)
		
class MotInterpolSplines(MotInterpolation):
	splines: List[Spline]

	def fromFile(self, file: BufferedReader):
		pos = file.tell()
		file.seek(pos + self.record.interpolationsOffset - 12)

		self.splines = []
		for _ in range(self.record.interpolationsCount):
			spline = Spline()
			spline.frame = read_uint16(file)
			read_uint16(file)	# dummy
			spline.value = read_float(file)
			spline.m0 = read_float(file)
			spline.m1 = read_float(file)
			self.splines.append(spline)

		file.seek(pos)
		
	def toKeyFrames(self) -> List[KeyFrame]:
		keyframes = []
		for spline in self.splines:
			keyframe = KeyFrame()
			keyframe.interpolationType = "BEZIER"
			keyframe.frame = spline.frame
			keyframe.value = spline.value
			keyframe.m0 = spline.m0
			keyframe.m1 = spline.m1
			keyframes.append(keyframe)
			keyframe.applyInterpolation = MotInterpolSplines.applyInterpolationToKeyFrame
		return keyframes

	def getKeyframeIndices(self) -> List[int]:
		return [spline.frame for spline in self.splines]
	
	@staticmethod
	def applyInterpolationToKeyFrame(prev: KeyFrameCombo|None, cur: KeyFrameCombo):
		if prev is None:
			return
		# hermit spline out/in slopes --> hermit spline out/in tangents
		m_prev = prev.mot.m1
		m_cur = cur.mot.m0
		hermit_prev = slopeToVec2D(m_prev)
		hermit_cur = slopeToVec2D(m_cur)
		# hermit spline out/in tangents --> bezier spline out/in tangents
		bezier_prev = hermitVecToBezierVec(hermit_prev)
		bezier_cur = hermitVecToBezierVec(hermit_cur) * -1
		# scale to frame distance
		xDist = cur.blend.co.x - prev.blend.co.x
		bezier_prev.x *= xDist
		bezier_cur.x *= xDist
		# offset point positions based on keyframe
		handle_prev_out = prev.blend.co + bezier_prev
		handle_cur_in = cur.blend.co + bezier_cur
		# set bezier handles
		cur.blend.interpolation = "BEZIER"
		prev.blend.handle_right_type = "FREE"
		cur.blend.handle_left_type = "FREE"
		prev.blend.handle_right = handle_prev_out
		cur.blend.handle_left = handle_cur_in

class MotInterpol5(MotInterpolSplines):
	def fromFile(self, file: BufferedReader):
		pos = file.tell()
		file.seek(pos + self.record.interpolationsOffset - 12)

		p = read_float(file)
		dp = read_float(file)
		m0 = read_float(file)
		dm0 = read_float(file)
		m1 = read_float(file)
		dm1 = read_float(file)
		self.splines = []
		for _ in range(self.record.interpolationsCount):
			spline = Spline()
			spline.frame = read_uint16(file)
			cp = read_uint16(file)
			cm0 = read_uint16(file)
			cm1 = read_uint16(file)
			spline.value = p + dp * cp
			spline.m0 = m0 + dm0 * cm0
			spline.m1 = m1 + dm1 * cm1
			self.splines.append(spline)

		file.seek(pos)
		
class MotInterpol6(MotInterpolSplines):
	def fromFile(self, file: BufferedReader):
		pos = file.tell()
		file.seek(pos + self.record.interpolationsOffset - 12)

		p = read_PgHalf(file)
		dp = read_PgHalf(file)
		m0 = read_PgHalf(file)
		dm0 = read_PgHalf(file)
		m1 = read_PgHalf(file)
		dm1 = read_PgHalf(file)
		self.splines = []
		for _ in range(self.record.interpolationsCount):
			spline = Spline()
			spline.frame = read_uint8(file)
			cp = read_uint8(file)
			cm0 = read_uint8(file)
			cm1 = read_uint8(file)
			spline.value = p + dp * cp
			spline.m0 = m0 + dm0 * cm0
			spline.m1 = m1 + dm1 * cm1
			self.splines.append(spline)
		
		file.seek(pos)
		
class MotInterpol7(MotInterpol6):
	def fromFile(self, file: BufferedReader):
		super().fromFile(file)

		absoluteFrame = 0
		for spline in self.splines:
			spline.frame += absoluteFrame
			absoluteFrame = spline.frame

class MotInterpol8(MotInterpolSplines):
	def fromFile(self, file: BufferedReader):
		pos = file.tell()
		file.seek(pos + self.record.interpolationsOffset - 12)

		p = read_PgHalf(file)
		dp = read_PgHalf(file)
		m0 = read_PgHalf(file)
		dm0 = read_PgHalf(file)
		m1 = read_PgHalf(file)
		dm1 = read_PgHalf(file)
		self.splines = []
		for _ in range(self.record.interpolationsCount):
			spline = Spline()
			spline.frame = read_uint16_be(file)
			cp = read_uint8(file)
			cm0 = read_uint8(file)
			cm1 = read_uint8(file)
			spline.value = p + dp * cp
			spline.m0 = m0 + dm0 * cm0
			spline.m1 = m1 + dm1 * cm1
			self.splines.append(spline)

		file.seek(pos)
