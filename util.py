import requests
from bs4 import BeautifulSoup,SoupStrainer
import logging
import re
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
