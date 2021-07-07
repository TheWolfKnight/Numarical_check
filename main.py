from sys import exit, argv
from typing import Optional, Union

import json, os, tempfile, glob


class _InputFileHandler(object):
	def __init__(self: object, filename: str):
		assert isinstance(filename, str), "Variable: \"filename\" was not a string"
		assert filename.endswith(".json"), "Variable: \"filename\" did not end with .json"
		self.filename = filename

	def getFiles(self: object) -> dict[str, Optional[str]]:
		"""
		Reads the input file and returns the json data as a dictionary\n
		@param self: object\n
		@return: dict[str, Optional[str]], the dictionary of keys and valuse to be used for the program
		"""
		with open(self.filename, "r") as r:
			data = json.loads(r.read())
			r.close()
		if (data["files"][0] == "*"):
			path = data["path"]
			data["files"] = glob.glob(f"{path}/*.txt")
		return data


class _DataHandler(object):
	def findData(filename: str) -> (Optional[str], Optional[int]):
		"""
		Finds and pulles the data from the file, and gives it with the line number from where it came\n
		@param filename: str, the file to be searched\n
		@return: (Optional[str], Optional[int]), touple of optional str and int, with the data and the line it came from
		"""
		assert os.path.isfile(filename), "Variable: \"filename\" is not a valid file path" 
		assert filename.endswith(".txt"), "Variable: \"filename\" did not end with .txt"
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
		"""
		Findes and removes duplicates from the list of ints\n
		@param numList: list[int], the list of ints to be filtered\n
		@return: (list[int], int), an touple of the filtered list and how many duplicats were removed
		"""
		assert isinstance(numList, list), "Variable : \"numList\" was not a list"
		res: list[int] = []
		dups = 0
		for i in range(len(numList)):
			for n in range(i+1, len(numList)):
				if (numList[i] == numList[n]):
					res.append(n)
					dups += 1
		return (res, dups)

	def removeCopies(numList: list[int], remList: list[int]) -> Union[list[int], bool]:
		"""
		Loops over the remList and removes the positions in numList, based on remLists values\n
		@param numList: list[int], the list to be removed from\n
		@param remList: list[int], contains the indexes of the items to be removed\n
		@return: Union[list[int], bool], returns the filterd list, or False if the were not changes made
		"""
		if (len(remList) == 0):
			return False
		res = list(map(lambda x: str(x), numList))
		for i in range(len(remList)-1, -1, -1):
			res.pop(remList[i])
		return res

	def reWriteInputFile(filename: str, data: list[int], startLine:int) -> None:
		"""
		Takes the original file and overwrites it with the filtered data\n
		@param filename: str, the original file\n
		@param data: list[int], the filtered data\n
		@param startLine: int, where the filtered data should go\n
		@return: None
		"""
		assert isinstance(filename, str), f"Variable: \"filename\" was not a string" 
		assert filename.endswith(".txt"), "Variable: \"filename\" did not end with .txt"
		assert isinstance(data, list), "Variable: \"data\" was not a list"
		assert isinstance(startLine, int), "Variable: \"startLine\" was not a int"
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
		td.close()

def main():
	found: int = 0
	args = list(map(lambda x: x.lower(), argv))
	try:
		file: str = args[args.index("-f")+1]
	except RuntimeError:
		exit({"Message": "Could not find file in arguments, no -f flag raised", "ExitCode": 1})
	
	try:
		inputFile = _InputFileHandler(file)
		fileData = inputFile.getFiles()
	except AssertionError as e:
		exit({"Message": f"{e}", "Function": "_InputFileHandler.getFiles()", "ExitCode": 2})

	rootPath = "." if fileData["path"] == None else fileData["path"]

	for file in fileData["files"]:
		try:
			data, line = _DataHandler.findData(f"{rootPath}/{file}")
		except AssertionError:
			print({"Message": f"There was no file in the path: {rootPath} named: {file}", "Function": "_DataHandler.findData()", "FailCode": 1})
			continue
		if (data == None):
			print({"Message": f"There were no provinces in the {file}", "Function": "_DataHandler.findData()", "FailCode": 2})
			continue
		data = data.split(" ")
		rem, tempFound = _DataHandler.findCopy(data)
		found += tempFound
		correctData = _DataHandler.removeCopies(data, rem)
		if (not correctData):
			print({"Message": f"there were no copys in the file {file}", "Function": "_DataHandler.findData()", "FailCode": 0})
			continue
		else:
			_DataHandler.reWriteInputFile(f"{rootPath}/{file}", correctData, line)
	return found

if __name__ == '__main__':
	found: int = main()
	exit({"Message": f"Task compleat, found {found} copys",	"ExitCode": 0})
