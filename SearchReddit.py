import requests
from bs4 import BeautifulSoup
import logging
import string 
import time
import re
import os.path
import base64
logging.getLogger().setLevel(logging.DEBUG)
_r_learnprogramming_url = re.compile(r'http://(www.)?reddit.com/r/learnprogramming')
def downloadUrl(url):
	logging.debug("Downloading url:{}".format(url))
	assert _r_learnprogramming_url.match(url)
	headers = {
				'User-Agent': 'SearchBot version 0.1'

			  }
	r = requests.get(url,headers=headers)
	if r.status_code != 200:
		raise Exception("Non-OK status code: {}".format(r.status.code) )
	return r.text

def parseText(html):
	bs = BeautifulSoup(html)
	return bs.select("div.usertext-body")[1].text

class Crawler():
	def __init__(self,startUrl,storeDir):
		self.startUrl = startUrl;
		self.storeDir = storeDir;
	@staticmethod
	def _makeAbsoluteUrl(url):
		return  'http://reddit.com'+url
	def crawl(self):
		logging.debug("Staring to crawl from page {}".format(self.startUrl))
		currentPageUrl  = self.startUrl
		while True:
			logging.debug("Current page {}".format(currentPageUrl))
			currentPage = downloadUrl(currentPageUrl)
			bs = BeautifulSoup(currentPage)
			allPostLinks = bs.find_all('a',attrs={'class':'title'})
			postLinks = [Crawler._makeAbsoluteUrl(link['href']) for link in allPostLinks]
			for postLink in postLinks:
				html = downloadUrl(postLink)
				storeFileName = os.path.join(self.storeDir,base64.b16encode(postLink))
				storeFile = open(storeFileName,'w')
				storeFile.write(html.encode('utf8'))
				time.sleep(2)
			logging.debug("First Post is {}".format(postLinks[0]))
			nextPageUrl = bs.find_all('a', rel = "next")[0]['href']
			
			currentPageUrl = nextPageUrl
			time.sleep(2)
