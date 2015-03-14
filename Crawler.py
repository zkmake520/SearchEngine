from bs4 import BeautifulSoup
import logging
import string 
import time
import re
import base64
import os.path
import argparse
from util import *


class Crawler():
	def __init__(self,startUrl,storeDir):
		self.startUrl = startUrl;
		self.storeDir = storeDir;
	@staticmethod
	def _makeAbsoluteUrl(url):
		return  'http://reddit.com'+url
	def crawl(self):
		logging.info("Staring to crawl from page {}".format(self.startUrl))
		currentPageUrl  = self.startUrl
		correctUrlCount = 0
		errorUrlCount = 0
		while True:
			if (correctUrlCount + errorUrlCount)% 100 == 0:
				logging.info("Crawled {} urls. Correct: {}  Error: {}".format(correctUrlCount + errorUrlCount,
					correctUrlCount,errorUrlCount))
			logging.info("Current page is:{}".format(currentPageUrl))
			currentPage = downloadUrl(currentPageUrl)
			bs = BeautifulSoup(currentPage)
			correctUrlCount += 1
			allPostLinks = bs.find_all('a',attrs={'class':'title'})
			postLinks = [Crawler._makeAbsoluteUrl(link['href']) for link in allPostLinks]
			try:
				for postLink in postLinks:
					html = downloadUrl(postLink)
					correctUrlCount +=1
					storeFileName = os.path.join(self.storeDir,base64.b16encode(postLink))
					storeFile = open(storeFileName,'w')
					storeFile.write(html.encode('utf8'))
					storeFile.close()
					time.sleep(2)
			#logging.getLogger(__name__).debug("First Post is {}".format(postLinks[0]))

			except Exception as e:
				errorUrlCount += 1
				logging.error("An error happended")
				logging.error(u"An error occured whiling crawling {}".format(currentPageUrl))
				logging.exception(e)
			nextPageUrl = bs.find_all('a', rel = "next")[0]['href']
			assert nextPageUrl is not None
			currentPageUrl = nextPageUrl
			time.sleep(2)

def main():
	logging.getLogger().setLevel(logging.INFO)
	logging.getLogger("requests").setLevel(logging.WARNING)
	parser = argparse.ArgumentParser(description = "Crawl /r/learnprogramming")
	parser.add_argument("--startUrl", dest = "startUrl",required=True)
	parser.add_argument("--storeDir", dest = "storeDir",required=True)
	args = parser.parse_args()
	crawler = Crawler(args.startUrl,args.storeDir)
	crawler.crawl()
if __name__ == "__main__":   # if invoke from command line
	main()
