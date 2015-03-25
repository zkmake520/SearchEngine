import logging
import praw
import praw.helpers
import logging
import argparse
import pickle
import os.path 
import time
from util import storeSub
from distutils.dir_util import mkpath
def crawlWithTimeStamp(storeDir,timeInterval,subReddit,startTimeStamp):
	mkpath(storeDir,mode=0755)
	r = praw.Reddit(user_agent='ZKBot v0.2 by/u/kanzhou')
	idToUrl,subIdDict,authorSubCount = dict(),dict(),dict()
	timeStampEnd = int(time.time())+7*3600 if startTimeStamp is None else int(startTimeStamp)  #different timestamp of UTC and losangeles
	timeStampStart = timeStampEnd - timeInterval
	while True:
		submissions = r.search("timestamp:{}..{}".format(timeStampStart,timeStampEnd),subreddit=subReddit,syntax="cloudsearch")
		subs = list(submissions)
		logging.debug("Get {} submissions in timeInterval {}..{}".format(len(subs),timeStampStart,timeStampEnd))
		storeSub(subs,subIdDict,authorSubCount,idToUrl,storeDir)
		timeStampEnd = timeStampStart
		timeStampStart = timeStampEnd - timeInterval

def main():
	logging.getLogger().setLevel(logging.DEBUG)
	logging.getLogger("requests").setLevel(logging.WARNING)
	argparser = argparse.ArgumentParser(description = "Crawl /r/learnprogramming")
	argparser.add_argument("--storeDir", dest = "storeDir",required=True)
	argparser.add_argument("--timeInterval", dest = "timeInterval",type = int,required=True)
	argparser.add_argument("--subReddit", dest = "subReddit",required=True)
	argparser.add_argument("--startTimeStamp", dest = "startTimeStamp",required=False,default=None)
	args = argparser.parse_args()
	crawlWithTimeStamp(args.storeDir,args.timeInterval,args.subReddit,args.startTimeStamp)
if __name__ == "__main__":   # if invoke from command line
	main()