import os
import settings
import boto3
from botocore.exceptions import ClientError
import tarfile
import shutil
import json

## Bucket to use
inBucketName = os.environ.get('S3_BUCKET_OUT')
inDirName = os.environ.get('WORK_DIR_IN')
outDirName = os.environ.get('WORK_DIR_OUT')
translator = os.environ.get('TRANSLATOR')

#Create working directories
if not os.path.exists(outDirName):
   os.mkdir(outDirName)

s3 = boto3.resource('s3')
bucket = s3.Bucket(inBucketName)
comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')

#List objects within a given prefix
for obj in bucket.objects.filter(Prefix='pre-sentiment/twitterData'):
   tgzFile = obj.key
   print(tgzFile)

   #Create working directories
   if not os.path.exists(inDirName+'/pre-sentiment'):
      os.mkdir(inDirName)
      os.mkdir(inDirName+'/pre-sentiment')

   # Get the object
   fileName = inDirName+'/'+tgzFile
   bucket.download_file(tgzFile, fileName)

   # Untar the object
   tar = tarfile.open(fileName)
   tar.extractall(path=inDirName)
   tar.close()

   # Tranlate data
   for filename in os.listdir(inDirName):
      if filename.endswith(".json") and os.stat(os.path.join(inDirName, filename)).st_size != 0: 
         pathFileName = os.path.join(inDirName, filename)
         print(pathFileName)
         with open(pathFileName,'r') as inFile:
            try:
               data = json.load(inFile)
               # TODO: Hash tags, retweet status and others to translate
               dataStr = data['text']
               sentiment = json.dumps(comprehend.detect_sentiment(Text=dataStr, LanguageCode='en'), sort_keys=True, indent=4)
	
               pathFileName = os.path.join(outDirName, filename)
               with open(pathFileName, 'w') as outFile:
                  json.dump(data, outFile, indent=4)
                  outFile.write(sentiment)
            except json.decoder.JSONDecodeError as e:
               print(e)
            inFile.close()
      else:
         continue

   # Retar data
   with tarfile.open(tgzFile[14:], "w:gz") as tar:
      tar.add(outDirName, arcname=os.path.basename(outDirName))

   # Copy to "translated" folder
   s3.meta.client.upload_file(tgzFile[14:], inBucketName, 'sentiment/'+tgzFile[14:])
   s3.Object(inBucketName, tgzFile).delete()


   # Cleanup
   try:
      os.remove(tgzFile[14:])
      shutil.rmtree(inDirName)
      shutil.rmtree(outDirName)
   except OSError as e:
      print ("Error: %s - %s." % (e.filename, e.strerror))

