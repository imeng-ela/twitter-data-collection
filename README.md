# twitter-data-collection
Pull twitter data and push to an AWS S3 bucket.  The thought here is to set up a cron job which periodically updates the list of tweets for various users in s3 for latter analysis.  There are 3 apps that should be set up as cron jobs.

1.  twitter-to-s3.py  This program pulls tweets for a list of user ids and puts resulting data in an S3 bucket.
2.  data-prep/translate.py  This program pulls the tweets created by twitter-to-s3.py and runs translations on the text.
3.  data-prep/sentiment.py  This programs takes the translated data and gathers sentiment data.

Bootstraping.
- Setup .aws/credentials for your bucket.  https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html
- Modifiy .env in twitter-to-s3 directory to your bucket which contains the .env file with further environment definitions to include. This bucket contains, the environment variable definitions below, plus the list of twitter names to collect tweets from.
```
# Keys for twitter account
CONSUMER_KEY = 'xxxxxxxxxxxxxxxx'
CONSUMER_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
ACCESS_TOKEN = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
ACCESS_TOKEN_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

INPUT_DIR = "/tmp/twitterIn/"
OUTPUT_DIR = "/tmp/twitterOut/"
WORK_DIR_IN = "/tmp/twitterWorkIn/"
WORK_DIR_OUT = "/tmp/twitterWorkOut/"
TWITTER_NAMES = "tnames.csv"

S3_BUCKET_OUT = "osint-twitter-data"
TRANSLATOR="google"
```
- CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN and ACCESS_TOKEN_SECRET are all values provided to you for your twitter developer account.  https://developer.twitter.com/
- INPUT_DIR is the processing direct for which various files are found.  Will create directory and populate it if not found.
- OUTPUT_DIR is where all the new tweets are saved while processing. Will create the directory if not found.
- WORK_DIR_IN is used by the translate program to copy the tweets and other configuration data.
- WORK_DIR_OUT is also used by the translate program to stor the translated tweets in.
- TWITTER_NAMES is a csv file which contains usernames to pull feeds from with the last known tweet id, i.e.  You can start at 1, like in the following example.  This file must be in your configuration bucket with the above .env file.
```
    elonmusk,1
    BillGates,1155855503949553666
```
- S3_BUCKET_OUT is S3 bucket where processing data is stored.  This needs to be set up in advance.
    - / directory is where raw tweet data is stored.  After it is translated the file is removed
    - /translated is the directory where translated data is stored.
    - /pre-sentiment is also where translated data is stored.  Once sentiment data has been gathered from it the file is removed.
    - /sentiment is the directory where sentiment data is stored.  Files contain the original tweet and sentiment data in json format.
TRANSLATOR is what translator to use.  Google cloud or AWS.  Accounts and permissions must be setup to do translation

