
import os
from typing import Dict

JapToEngMap: Dict[str, str] = {}
def initializeJapToEng():
	if JapToEngMap:
		return
	curDir = os.path.dirname(os.path.abspath(__file__))
	translationsFile = os.path.join(curDir, "japToEng.txt")
	with open(translationsFile, "r", encoding="utf-8") as f:
		lines = f.readlines()
	count = len(lines) // 3
	for i in range(count):
		japStr = lines[i * 3].strip()
		engStr = lines[i * 3 + 1].strip()
		JapToEngMap[japStr] = engStr

def japToEng(japStr: str) -> str:
	initializeJapToEng()
	return JapToEngMap[japStr] if japStr in JapToEngMap else "?"
