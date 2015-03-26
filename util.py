import requests
from bs4 import BeautifulSoup,SoupStrainer
import logging
import re
import os
import json
_r_learnprogramming_url = re.compile(r'http://(www.)?reddit.com/r/learnprogramming')
def downloadUrl(url):
	logging.info("Downloading url:{}".format(url))
	assert _r_learnprogramming_url.match(url)
	headers = {
				'User-Agent': 'SearchBot version 0.1'

			  }
	r = requests.get(url,headers=headers)
	if r.status_code != 200:
		raise Exception("Non-OK status code: {}".format(r.status.code) )
	return r.text

_parseOnlyPart = SoupStrainer("div",{"class": "entry unvoted"})
def parseRedditPost(html):
	bs = BeautifulSoup(html,parse_only = _parseOnlyPart)
	return bs.select("div.usertext-body")[1].text

def storeSub(submission,subIdDict,authorSubCount,idToUrl,storeDir):
	i=0
	for sub in submission:
		if sub.id not in subIdDict:   # if this submission is not repeated
			subIdDict[sub.id] = True
			idToUrl[sub.id] = sub.permalink
			with open(os.path.join(storeDir,sub.id),"w") as file:
				authorName = sub.author.name if sub.author != None else ""
				try:
					#userLink = r.get_redditor(authorName)._url
					userLink = "http://www.reddit.com/user/" + authorName+"/"
					authorSubCount[authorName] = authorSubCount[authorName]+1 if authorName in authorSubCount else 1
					json.dump({"author":authorName.encode("utf8"),"userlink":userLink.encode("utf8"),"url":sub.permalink.encode("utf8"),"title:":sub.title.encode("utf8"),"text":sub.selftext.encode("utf8")},file,ensure_ascii=False)
				except Exception as e:
					logging.exception(e)
				file.close()