import os
import time
import settings
import boto3
import json

from TwitterSearch import *
from tempfile import NamedTemporaryFile

import tarfile
import shutil
import csv

# Get some environment variables
twitterNamesFile = os.environ.get('TWITTER_NAMES')
inDirName = os.environ.get('INPUT_DIR')
outDirName = os.environ.get('OUTPUT_DIR')
configBucketName = os.environ.get('S3_CONFIG_BUCKET')
outBucketName = os.environ.get('S3_BUCKET_OUT')

#Create working directories
if not os.path.exists(inDirName):
    os.mkdir(inDirName)
    print("Directory " , inDirName ,  " Created ")
else:
    print("Directory " , inDirName ,  " already exists")

if not os.path.exists(outDirName):
    os.mkdir(outDirName)
    print("Directory " , outDirName ,  " Created ")
else:
    print("Directory " , outDirName ,  " already exists")

# Download from S3 names list 
configBucketName = os.environ.get('S3_CONFIG_BUCKET')
s3 = boto3.resource('s3')
try:
   bucket = s3.Bucket(configBucketName).download_file(twitterNamesFile, inDirName+'/'+twitterNamesFile)
except botcore.exceptions.ClientError as e:
   if e.response['Error']['Code'] == "404":
      print("The object does not exist.")
   else:
      raise

# Need to update the names list file to keep track of last message id.  We do this with a temp file
tempfile = NamedTemporaryFile(mode='w', delete=False)
fields = ['name', 'lastId']

# Get the tweets for all the users in the Names list
with open(inDirName+'/'+twitterNamesFile, mode='r') as csv_file, tempfile:
   tempDict = csv.DictWriter(tempfile, fieldnames=fields)
   namesDict = csv.DictReader(csv_file, fieldnames=fields)

   for row in namesDict:
      name = row["name"]
      lastId = int(row["lastId"])
      try:
         tuo = TwitterUserOrder(name) # create a TwitterUserOrder
         tuo.set_exclude_replies(False)
         tuo.set_include_rts(True)
         tuo.set_since_id(lastId)

         # Secret tokens are environment variables
         ts = TwitterSearch(
         consumer_key = os.environ.get('CONSUMER_KEY'),
         consumer_secret = os.environ.get('CONSUMER_SECRET'),
         access_token = os.environ.get('ACCESS_TOKEN'),
         access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')
         )

         # this is where the fun actually starts :)
         maxid = lastId
         for tweet in ts.search_tweets_iterable(tuo):
            outfilename=outDirName+name+'-'+tweet['id_str']+'.json'
            fo = open(outfilename,"w+")
            #fo.write(str(tweet) )
            json.dump(tweet, fo)
            id = tweet['id']
            if(id > maxid):
               maxid = id
         row["lastId"] = maxid
         tempDict.writerow(row)

      except TwitterSearchException as e: # take care of all those ugly errors if there are some
         tempDict.writerow(row)
         print(e)

# Copy the temp file to replace the names list with the last updated message id
shutil.move(tempfile.name, inDirName+'/'+twitterNamesFile)

# Copy the names list file back to S3
s3.meta.client.upload_file(inDirName+'/'+twitterNamesFile, configBucketName, twitterNamesFile)

# Tar up the files
timestr = time.strftime("%Y%m%d-%H%M%S")
twitterTarName = 'twitterData'+timestr+'.tgz'
with tarfile.open(twitterTarName, "w:gz") as tar:
   tar.add(outDirName, arcname=os.path.basename(outDirName))   

# Copy the tweets to the S3 bucket
s3.meta.client.upload_file(twitterTarName, outBucketName, twitterTarName)

# Clean up local versions of tweets.
try:
    os.remove(twitterTarName)
    shutil.rmtree(outDirName)
except OSError as e:
    print ("Error: %s - %s." % (e.filename, e.strerror))

