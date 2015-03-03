import os.path
import os
import json
import argparse
from util import *
import base64
import logging
# todo : remove this assumptions
# Indexer assumes thast collection fits in memory()
class Indexer:
	def __init__(self):
		self.invertedIndex = dict()
		self.forwardIndex = dict()
		self.urlToId = dict()     #url is too long
		self.docCount = 0
	# TOdo: remove this assumptions	
	# assumes that adddocument () is never called twice for a document
	# assumes that a document has an unique url
	# parsed text is a listed of words
	def addDocument(self,url,parsedText):
		self.docCount += 1
		currentId = self.docCount
		self.urlToId[currentId] = url;
		self.forwardIndex[currentId] = parsedText
		for position,word in enumerate(parsedText):
			if word not in self.invertedIndex:
				self.invertedIndex[word] = []
			self.invertedIndex[word].append((position,currentId))

	# dump as json
	def dumpToDisk(self,IndexDir):
		invertedIndexFileName = os.path.join(IndexDir,"inverted")
		forwardIndexFileName = os.path.join(IndexDir,"forward")
		urlToIdFileName = os.path.join(IndexDir,"urlToId")
		invertedIndexFile = open(invertedIndexFileName,"w")
		forwardIndexFile = open(forwardIndexFileName,"w")	
		urlToIdFile = open(urlToIdFileName,"w")
		json.dump(self.urlToId,urlToIdFile,indent=4)
		json.dump(self.invertedIndex,invertedIndexFile,indent=4)
		json.dump(self.forwardIndex,forwardIndexFile,indent=4)

def createIndexDir(storedDocumentDir,indexDir):
	indexer = Indexer()
	for fileName in os.listdir(storedDocumentDir):
		logging.info(u"Adding Document: {}".format(base64.b16decode(fileName)))
		openFile = open(os.path.join(storedDocumentDir,fileName)) # TODO:word are separated not only be space
		parsedText = parseRedditPost(openFile.read()).split(" ")
		indexer.addDocument(base64.b16decode(fileName),parsedText)
	indexer.dumpToDisk(indexDir)

def main():
	logging.getLogger().setLevel(logging.INFO)
	parser = argparse.ArgumentParser(description = "Index/r/learnprogramming")
	parser.add_argument("--storedDocumentDir", dest = "storedDocumentDir")
	parser.add_argument("--indexDir", dest = "indexDir")
	args = parser.parse_args()
	createIndexDir(args.storedDocumentDir,args.indexDir)

if __name__ == "__main__":   # if invoke from command line
	main()