import json , csv , time
from collections import OrderedDict
import tweepy

class GetTweetsObject:

    def __init__(self,path_json):
        d = OrderedDict()
        with open(path_json,"r") as f:
            d = json.loads(f.read())
        api_key = d["api_key"]
        api_secret = d["api_secret"]
        access_token = d["access_token"]
        access_token_secret = d["access_token_secret"]

        auth = tweepy.OAuthHandler(api_key,api_secret)
        auth.set_access_token(access_token,access_token_secret)
        self.__api = tweepy.API(auth)

    def get_tweets(self,username,exclude_replies=True,avoid_api_regulation=False):
        self.tweets = []
        for tweet in tweepy.Cursor(self.__api.user_timeline,
            screen_name = username,tweet_mode="extended",
            exclude_replies = exclude_replies).items():
            if (not tweet.retweeted) and ('RT @' not in tweet.full_text):
                self.tweets.append(tweet)
            # User Timeline API is allowed us to get 900 tweets / 900 sec (15 minutes)
            if avoid_api_regulation:
                time.sleep(1)
