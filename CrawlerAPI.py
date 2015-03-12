import praw
import praw.helpers
import logging
import argparse
import pickle
import os.path 
from collections import defaultdict
def crawl(storeDir):
	r = praw.Reddit(user_agent='ZKBot v0.2')
	idToUrl,subIdDict,authorSubCount = dict(),dict(),dict()
	getMethodName = ["get_hot","get_new","get_top_from_all","get_top_from_year","get_top_from_month","get_top_from_week","get_top_from_day"]
	for methodName in getMethodName:
		method = getattr(r.get_subreddit("learnprogramming"),methodName)
		submission = method(limit=1000)
		storeSub(submission,subIdDict,authorSubCount,idToUrl,storeDir)
	storeAuthorCount(authorSubCount,storeDir)
	storeUrl(idToUrl,storeDir)	

def storeAuthorCount(authorSubCount,storeDir):
	with open(os.path.join(storeDir,"authorSubCount"),"w") as file:
		pickle.dump(authorSubCount,file)
	file.close()

def storeUrl(idToUrl,storeDir):
	with open(os.path.join(storeDir,"idToUrl"),"w") as file:
		pickle.dump(idToUrl,file)
	file.close()

def storeSub(submission,subIdDict,authorSubCount,idToUrl,storeDir):
	for sub in submission:
		if sub.id not in subIdDict:   # if this submission is not repeated
			subIdDict[sub.id] = True
			idToUrl[sub.id] = sub.permalink
			with open(os.path.join(storeDir,sub.id),"w") as file:
				authorName = sub.author.name.encode("utf8") if sub.author != None else ""
				try:
					#userLink = r.get_redditor(authorName)._url
					userLink = "http://www.reddit.com/user/" + authorName+"/"
					authorSubCount[authorName] = authorSubCount[authorName]+1 if authorName in authorSubCount else 1
					pickle.dump([authorName,userLink.encode("utf8"),sub.title.encode("utf8"),sub.selftext.encode("utf8")],file)
				except Exception as e:
					logging.exception(e)
				file.close()

def crawlRepeatedly(storeDir):
	r = praw.Reddit(user_agent="ZKBot v0.2")
	idToUrl,subIdDict,authorSubCount = dict(),dict(),dict()	
	submissions = praw.helpers.submission_stream(r,"learnprogramming")
	storeSub(submissions,subIdDict,authorSubCount,idToUrl,storeDir)
	storeAuthorCount(submissions,authorSubCount,storeDir)
	storeUrl(submissions,idToUrl,storeDir)	

def main():
	logging.getLogger().setLevel(logging.INFO)
	logging.getLogger("requests").setLevel(logging.WARNING)
	argparser = argparse.ArgumentParser(description = "Crawl /r/learnprogramming")
	#argparser.add_argument("--startUrl", dest = "startUrl",required=True)
	argparser.add_argument("--storeDir", dest = "storeDir",required=True)
	args = argparser.parse_args()
	crawlRepeatedly(args.storeDir)
if __name__ == "__main__":   # if invoke from command line
	main()