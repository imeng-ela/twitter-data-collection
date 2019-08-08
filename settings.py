#settings.py
import os
from dotenv import load_dotenv
from pathlib import Path  # python3 only
import boto3


load_dotenv()

bucketName = os.environ.get('S3_CONFIG_BUCKET')
print(bucketName)

home = str(Path.home())
envFile = home+'/'+'.env'

s3 = boto3.resource('s3')
try:
   bucket = s3.Bucket(bucketName).download_file('.env', envFile)
except botcore.exceptions.ClientError as e:
   if e.response['Error']['Code'] == "404":
      print("The object does not exist.")
   else:
      raise

load_dotenv(dotenv_path=envFile)

