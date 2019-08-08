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

#Create working directories
if not os.path.exists(outDirName):
   os.mkdir(outDirName)

s3 = boto3.resource('s3')
translate = boto3.client(service_name='translate', region_name='us-east-1', use_ssl=True)
bucket = s3.Bucket(inBucketName)

## List objects within a given prefix
for obj in bucket.objects.filter(Prefix='twitterData'):
   tgzFile = obj.key
   print(tgzFile)

   #Create working directories
   if not os.path.exists(inDirName):
      os.mkdir(inDirName)

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
               srcLang = data['lang']
               if srcLang == 'und':
                  print("Cannot translate tweet.  Language was not detected by twitter")
               elif srcLang != 'en':
                  try:
                     result = translate.translate_text(Text=dataStr, SourceLanguageCode=srcLang, TargetLanguageCode="en")
                     data['text'] = result.get('TranslatedText')
                     print(srcLang+': '+dataStr)
                     print('en: '+str(data['text']))
                  except ClientError as e:
                     print("Language " + srcLang + " is not supported by amazon translate")
               pathFileName = os.path.join(outDirName, filename)
               with open(pathFileName, 'w') as outFile:
                  json.dump(data, outFile, indent=4)
            except json.decoder.JSONDecodeError as e:
               print(e)
            inFile.close()
      else:
         continue

   # Retar data
   with tarfile.open(tgzFile, "w:gz") as tar:
      tar.add(outDirName, arcname=os.path.basename(outDirName))

   # Copy to "translated" folder
   s3.meta.client.upload_file(tgzFile, inBucketName, 'translated/'+tgzFile)

   # Move original to "raw" folder
   s3.meta.client.upload_file(inDirName+'/'+obj.key, inBucketName, 'raw/'+tgzFile)
   s3.Object(inBucketName, tgzFile).delete()

   # Cleanup
   try:
      os.remove(tgzFile)
      shutil.rmtree(inDirName)
      shutil.rmtree(outDirName)
   except OSError as e:
      print ("Error: %s - %s." % (e.filename, e.strerror))

