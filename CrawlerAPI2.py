import logging
import praw
import praw.helpers
import logging
import argparse
import pickle
import os.path 
import time
from CrawlerAPI import storeSub
from distutils.dir_util import mkpath
def crawlWithTimeStamp(storeDir,timeInterval,subReddit):
	mkpath(storeDir,mode=0755)
	r = praw.Reddit(user_agent='ZKBot v0.2 by/u/kanzhou')
	idToUrl,subIdDict,authorSubCount = dict(),dict(),dict()
	timeStampEnd = int(time.time())+7*3600  #different timestamp of UTC and losangeles
	timeStampStart = timeStampEnd - timeInterval
	while True:
		submissions = r.search("timestamp:{}..{}".format(timeStampStart,timeStampEnd),subreddit=subReddit,syntax="cloudsearch")
		storeSub(submissions,subIdDict,authorSubCount,idToUrl,storeDir)
		logging.debug("Get {} submissions in timeInterval {}..{}".format(len(list(submissions)),timeStampStart,timeStampEnd))

		timeStampEnd = timeStampStart
		timeStampStart = timeStampEnd - timeInterval

def main():
	logging.getLogger().setLevel(logging.DEBUG)
	logging.getLogger("requests").setLevel(logging.WARNING)
	argparser = argparse.ArgumentParser(description = "Crawl /r/learnprogramming")
	argparser.add_argument("--storeDir", dest = "storeDir",required=True)
	argparser.add_argument("--timeInterval", dest = "timeInterval",type = int,required=True)
	argparser.add_argument("--subReddit", dest = "subReddit",required=True)
	args = argparser.parse_args()
	crawlWithTimeStamp(args.storeDir,args.timeInterval,args.subReddit)
if __name__ == "__main__":   # if invoke from command line
	main()