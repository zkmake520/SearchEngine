#! /usr/bin/env python
import os.path
import os
import json
import argparse
from util import *
from collections import defaultdict
import base64
import logging
import sys
from LangProc import docTerms
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

	def findDocument_AND(self,queryStr):
		documentIdList = defaultdict(lambda:0)
		for word in queryStr:
			for id in set([item[1] for item in self.invertedIndex.get(word,[])]):
				documentIdList[id] += 1
		return [docId for docId,cnt in documentIdList.iteritems() if cnt ==len(queryStr)]

	def getSnippets(self,queryStr,id):
		id = unicode(id)
		currentWindow = [-1]*(len(queryStr))
		keyLen = 0
		minWindow = []
		minSize = sys.maxint
		bestIndenticalWordSize = 0
		for pos,word in enumerate(self.forwardIndex[id]):
			if word in queryStr:
				currentWindow[queryStr.index(word)] = pos
				if  -1 not in currentWindow:
					start = min(currentWindow)
					end = pos
					indenticalWordSize = len(set(self.forwardIndex[id][start : end+1])) 
					if(minSize >  end-start+1) or (indenticalWordSize > bestIndenticalWordSize and minSize+2 >= end-start+1):
						minWindow = currentWindow[:] 
						minSize = end-start + 1 
						bestIndenticalWordSize = indenticalWordSize
		docLength = len(self.forwardIndex[id])
		snippetsStart = max(min(minWindow)-8,0)
		snippetsEnd = min(docLength, max(minWindow)+1+8)
		return [(word,word in queryStr) for word in self.forwardIndex[id][snippetsStart:snippetsEnd]] #excellent implemention:return list of truple make critical word be true in turple

	def getDocumentText(self,id):
		return self.forwardIndex[unicode(id)]

	def getUrl(self,id):  # here we load all data from files thus the type is string !
		return self.urlToId[unicode(id)]	

def createIndexDir(storedDocumentDir,indexDir):
	indexer = Indexer()
	for fileName in os.listdir(storedDocumentDir):
		logging.info(u"Adding Document: {}".format(base64.b16decode(fileName)))
		openFile = open(os.path.join(storedDocumentDir,fileName)) # TODO:word are separated not only be space
		parsedText = docTerms(parseRedditPost(openFile.read()))
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