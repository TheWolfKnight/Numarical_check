from sys import exit, argv
from typing import Optional, Union

import json, os, tempfile

FOUND: int = 0

class _InputFileHandler(object):
	def __init__(self: object, filename: str):
		assert isinstance(filename, str) and filename.endswith(".json")
		self.filename = filename

	def getFiles(self: object) -> dict[str, Optional[Union[str, bool]]]:
		with open(self.filename, "r") as r:
			data = json.loads(r.read())
			r.close()
		return data


class _DataHandler(object):
	def findData(filename: str) -> (Optional[str], Optional[int]):
		assert os.path.isfile(filename) and filename.endswith(".txt")
		foundFlag = False
		lineNumber = 1
		with open(filename, "r") as f:
			for line in f.readlines():
				if (foundFlag):
					return (line.strip(), lineNumber)
				if (line == "	provinces={\n"):
					foundFlag = True
				lineNumber += 1
			return (None, None)

	def findCopy(numList: list[int]) -> (list[int], int):
		res = list(map(lambda x: x, numList))
		dups = 0
		for i in range(len(numList)):
			# print(len(res), "\n", res)
			for n in range(i+1, len(numList)):
				if (numList[i] == numList[n]):
					res.pop(n)
					dups += 1
		return (res, dups)

	def reWriteInputFile(filename: str, data: list[int], startLine:int) -> None:
		assert isinstance(filename, str) and filename.endswith(".txt")
		assert isinstance(data, list)
		assert isinstance(startLine, int)
		currLine = 1
		corretData = "		" + " ".join(data) + "\n"
		with tempfile.TemporaryDirectory() as td:
			tmpFileName = os.path.join(td, "tmp.txt")
			with open(tmpFileName, "w") as tf:
				with open(filename, "r") as rf:
					for line in rf.readlines():
						if (currLine == startLine):
							tf.writelines(corretData)
							currLine += 1
						else:
							tf.writelines(line)
							currLine += 1
					rf.close()
				tf.close()

			with open(tmpFileName, "r") as tf:
				with open(filename, "w") as wf:
					tf.seek(0)
					wf.write(tf.read())
					wf.close()
				tf.close()

def main():
	global FOUND
	args = list(map(lambda x: x.lower(), argv))
	try:
		file: str = args[args.index("-f")+1]
	except RuntimeError:
		exit({"Message": "Could not find file in arguments, no -f flag raised", "ExitCode": 1})
	
	try:
		inputFile = _InputFileHandler(file)
		fileData = inputFile.getFiles()
	except AssertionError:
		exit({"Message": f"Could not fine the file {file}", "ExitCode": 2})

	rootPath = "." if fileData["path"] == None else fileData["path"]

	for file in fileData["files"]:
		try:
			data, line = _DataHandler.findData(f"{rootPath}/{file}")
		except AssertionError:
			print(f"There was no file in the path: {rootPath} named: {file}")
			continue
		if (data == None):
			exit({"Message": "There were no provinces in the file", "ExitCode": 4})
		data = data.split(" ")
		res, FOUND = _DataHandler.findCopy(data)
		_DataHandler.reWriteInputFile(file, data, line)

if __name__ == '__main__':
	found: int = FOUND
	main()
	exit({"Message": f"Task compleat, found {found} copys",	"ExitCode": 0})
