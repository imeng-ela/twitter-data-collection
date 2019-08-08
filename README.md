# twitter-to-s3
Pull twitter data and push to an AWS S3 bucket.  The thought here is to set up a cron job which periodically updates the list of tweets for various users in s3 for latter analysis.

Bootstraping.
- Setup .aws/credentials for your bucket.
- Modifiy .env in this directory to your bucket which contains the .env file with further environment definitions to include.
```
    CONSUMER_KEY = 'xxxxx'
    CONSUMER_SECRET = 'xxxxxxxxxx'
    ACCESS_TOKEN = 'xxxxxxxxxx'
    ACCESS_TOKEN_SECRET = 'xxxxxxxxxx'

    INPUT_DIR = "/tmp/twitterIn/"
    OUTPUT_DIR = "/tmp/twitterOut/"
    TWITTER_NAMES = "tnames.csv"

    S3_BUCKET_OUT = "twitter-data"
```
- Create a csv file (TWITTER_NAMES) which is a file of usernames to pull feeds from with the last known tweet id, i.e.  You can start at 1, like in the following example.  This file must be in your configuration bucket with the above .env file.

```
    elonmusk,1
    BillGates,1155855503949553666
```
Finally you'll need to setup a bucket to write the tweets to (S3_BUCKET_OUT).
