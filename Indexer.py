#! /usr/bin/env python
import os.path
import os
import argparse
import pickle
from util import *
from collections import defaultdict
import base64
import logging
import sys
import json
import shelve
#from FeatureExtraction import Tf_Idf
from LangProc import docTerms
# todo : remove this assumptions
# Indexer assumes thast collection fits in memory()
class DBMIndex:
	pass
class BaseIndexer():
	def __init__(self):
		self.invertedIndex = defaultdict(list)
		self.forwardIndex = dict()
		self.idToUrl = dict()     #url is too long
		self.docCount =0

class ShelveIndexer():
	def __init__(self):
		self.invertedIndex = None
		self.forwardIndex = None 
		self.idToUrl = None     #url is too long
		self.urlToId =dict() 
		self.docCount =0

	def addDocument(self,url,parsedText):
		assert url.encode("utf8") not in self.urlToId
		self.docCount += 1
		currentId = self.docCount
		self.urlToId[url.encode("utf8")] = currentId
		self.idToUrl[str(currentId)] = url;
		self.forwardIndex[str(currentId)] = parsedText
		for position,term in enumerate(parsedText):
			stem = term.stem.encode("utf8")
			documents = self.invertedIndex[stem] if stem in self.invertedIndex else []
			documents.append((position,currentId)) 
			self.invertedIndex[stem] = documents

	def startIndexer(self,indexDir):
		self.invertedIndex = shelve.open(os.path.join(indexDir,"invertedIndex"),'c')
		self.forwardIndex = shelve.open(os.path.join(indexDir,"forwardIndex"),'c')
		self.idToUrl = shelve.open(os.path.join(indexDir,"idToUrl"),'c')

	def finishIndexer(self):
		self.invertedIndex.close()
		self.forwardIndex.close()
		self.idToUrl.close()

	def loadIndexer(self,indexDir):
		self.invertedIndex = shelve.open(os.path.join(indexDir,"invertedIndex"),'r')
		self.forwardIndex = shelve.open(os.path.join(indexDir,"forwardIndex"),'r')
		self.idToUrl = shelve.open(os.path.join(indexDir,"idToUrl"),'r')

	def getDocumentOfQuery(self,query):
		return self.invertedIndex.get(query.stem.encode("utf8"),[])

	def getDocumentOfId(self,id):
		return self.forwardIndex.get(str(id),[])

	def getUrl(self,id):  # here we load all data from files thus the type is string !
		return self.idToUrl[str(id)]	


class MemoryIndexer():
	def __init__(self):
		self.invertedIndex = defaultdict(list)
		self.forwardIndex = dict()
		self.idToUrl = dict()     #url is too long
		self.docCount =0
	# TOdo: remove this assumptions	
	# assumes that adddocument () is never called twice for a document
	# assumes that a document has an unique url
	# parsed text is a listed of terms
	def addDocument(self,url,parsedText):
		self.docCount += 1
		currentId = self.docCount
		self.idToUrl[currentId] = url;
		self.forwardIndex[currentId] = parsedText
		for position,term in enumerate(parsedText):
			self.invertedIndex[term].append((position,currentId))
	# dump as json
	def dumpToDisk(self,IndexDir):
		def pickleDumpToFile(source,fileName):
			file = open(os.path.join(IndexDir,fileName),"w")
			pickle.dump(source,file)

		pickleDumpToFile(self.idToUrl,"idToUrl")
		pickleDumpToFile(self.invertedIndex,"inverted")
		pickleDumpToFile(self.forwardIndex,"forward")

	def loadFromDisk(self,indexDir):
		def pickleLoadFromFile(fileName):
			file = open(os.path.join(indexDir,fileName),"r")
			return pickle.load(file)
		self.invertedIndex=pickleLoadFromFile("inverted")
		self.idToUrl=pickleLoadFromFile("idToUrl")
		self.forwardIndex=pickleLoadFromFile("forward")

	def getDocumentOfQuery(self,query):
		return self.invertedIndex.get(query,[])

	def getDocumentOfId(self,id):
		return self.forwardIndex.get(id,[])

	def getUrl(self,id):  # here we load all data from files thus the type is string !
		return self.idToUrl[str(id)]	

			
class Searcher():
	def __init__(self,indexDir,implemention=ShelveIndexer):
		self.index = implemention()
		self.index.loadIndexer(indexDir)

	def findDocument_AND(self,queryStr):
		documentIdList = defaultdict(lambda:0)
		for term in queryStr:
			for id in set([item[1] for item in self.index.getDocumentOfQuery(term)]):
				documentIdList[id] += 1
		return [docId for docId,cnt in documentIdList.iteritems() if cnt ==len(queryStr)]

	def getUrl(self,id):
		return self.index.idToUrl[str(id)]

	def getSnippets(self,queryStr,id):
		currentWindow = [-1]*(len(queryStr))
		keyLen = 0
		minWindow = []
		minSize = sys.maxint
		bestIndenticaltermSize = 0
		for pos,term in enumerate(self.index.getDocumentOfId(id)):
			if term in queryStr:
				currentWindow[queryStr.index(term)] = pos
				if  -1 not in currentWindow:
					start = min(currentWindow)
					end = pos
					indenticaltermSize = len(set(self.index.getDocumentOfId(id)[start : end+1])) 
					if(minSize >  end-start+1) or (indenticaltermSize > bestIndenticaltermSize and minSize+2 >= end-start+1):
						minWindow = currentWindow[:] 
						minSize = end-start + 1 
						bestIndenticaltermSize = indenticaltermSize
		docLength = len(self.index.getDocumentOfId(id))
		snippetsStart = max(min(minWindow)-10,0)
		snippetsEnd = min(docLength, max(minWindow)+1+10)
		return [(term.originalWord,term in queryStr) for term in self.index.getDocumentOfId(id)[snippetsStart:snippetsEnd]] #excellent implemention:return list of truple make critical term be true in turple

'''
def createIndexDir(storedDocumentDir,indexDir):
	indexer = MemoryIndexer()
	indexCount = 0
	for fileName in os.listdir(storedDocumentDir):
		indexCount +=1
		if indexCount % 100 ==0:
			logging.info(u"Indexed {} documents".format(indexCount))
		logging.info(u"Adding Document: {}".format(base64.b16decode(fileName)))
		openFile = open(os.path.join(storedDocumentDir,fileName))
		parsedText = docTerms(parseRedditPost(openFile.read()))
		indexer.addDocument(base64.b16decode(fileName),parsedText)
	indexer.dumpToDisk(indexDir)
'''
def createIndexDirApi(storedDocumentDir,indexDir,implemention=ShelveIndexer):
	indexer = implemention()
	indexer.startIndexer(indexDir)
	indexCount = 0
	for fileName in os.listdir(storedDocumentDir):
		#logging.info(u"Adding Document: {}".format(base64.b16decode(fileName)))
		openFile = open(os.path.join(storedDocumentDir,fileName))
		try:
			jsonFile = json.load(openFile)
			parsedText = docTerms(jsonFile['text'])
			indexer.addDocument(jsonFile['url'],parsedText)
			indexCount +=1
			if indexCount % 100 ==0:
				logging.info(u"Indexed {} documents".format(indexCount))
		except Exception as e:
			logging.exception(e)
		openFile.close()
	indexer.finishIndexer()

def main():
	logging.getLogger().setLevel(logging.INFO)
	parser = argparse.ArgumentParser(description = "Index/r/learnprogramming")
	parser.add_argument("--storedDocumentDir", dest = "storedDocumentDir", required= True)
	parser.add_argument("--indexDir", dest = "indexDir", required = True)
	args = parser.parse_args()
	createIndexDirApi(args.storedDocumentDir,args.indexDir)

if __name__ == "__main__":   # if invoke from command line
	main()