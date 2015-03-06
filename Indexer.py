#! /usr/bin/env python
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
		self.docCount =0
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
		def jsonDumpToFile(source,fileName):
			file = open(os.path.join(IndexDir,fileName),"w")
			json.dump(source,file,indent=4)

		jsonDumpToFile(self.urlToId,"urlToId")
		jsonDumpToFile(self.invertedIndex,"inverted")
		jsonDumpToFile(self.forwardIndex,"forward")
class Searcher():
	def __init__(self,indexDir):
		self.invertedIndex = dict()
		self.forwardIndex = dict()
		self.urlToId = dict()     #url is too long
		self.docCount = 0
		def jsonLoadFromFile(fileName):
			file = open(os.path.join(indexDir,fileName),"r")
			return json.load(file)

		self.invertedIndex=jsonLoadFromFile("inverted")
		self.urlToId=jsonLoadFromFile("urlToId")
		self.forwardIndex=jsonLoadFromFile("forward")
	def findDocument(self,queryStr):
		return sum([self.invertedIndex[word] for word in queryStr],[])
	def getUrl(self,id):  # here we load all data from files thus the type is string !
		return self.urlToId[str(id)]	
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
	parser.add_argument("--storedDocumentDir", dest = "storedDocumentDir", required= True)
	parser.add_argument("--indexDir", dest = "indexDir", required = True)
	args = parser.parse_args()
	createIndexDir(args.storedDocumentDir,args.indexDir)

if __name__ == "__main__":   # if invoke from command line
	main()