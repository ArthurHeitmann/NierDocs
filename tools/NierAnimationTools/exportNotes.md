# Export

2 Modes: Save, Patch

Steps:
1. Collect all objects with animations
	- Searchable: armature & its bones / all armature FCurves
2. Sort by Bone ID?
3. For each FCurve make a Record with interpolation data
	- get bone index, property index, flag || DEFAULT_FLAG TODO
	- Determine interpolation type
		- 1 Keyframe
			- `0x0`
			- constant
		- Baked animation / all frames are 1 frame apart
			- `0x1`
			- list of n values
		- else
			- `0x4`
			- Hermit interpolated values
			- For each frame:
				- Transform bezier tangents --> hermit slopes
					- for both handles subtract KF value
					- normalize on X axis
					- Check whether X-normalized tangents have length 1/3
					- bezier points --> hermit tangents
					- hermit tangents --> slopes
3. (if in patch mode) Inject all other existing records
4. Determine all interpolation offsets based relative to record
5. Make header
	- hash | DEFAULT_HASH TODO
	- flag | DEFAULT_FLAG TODO
	- max frame
	- file name or scene name? TODO
	- records offset based on animName (24 + animName.length + 9 OR 44)
5. Write
6. ???
7. Profit
