#!/usr/bin/env python
import tweepy
import os
from datetime import datetime
from pathlib import Path

def main():

    #時刻制御
    if datetime.now().hour() > 22 or datetime.now().hour() < 7:
        exit()

    #OAuth
    api_key = os.environ.get("API_KEY")
    api_secret = os.environ.get("API_SECRET")
    access_token = os.environ.get("ACCESS_TOKEN")
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
    auth = tweepy.OAuthHandler(api_key,api_secret)
    auth.set_access_token(access_token,access_token_secret)
    api = tweepy.API(auth)

    #Call Tasks
    tweet_articles(api,"tweets/id_list.txt")

def tweet_articles(api,list_path):
    # リストから順番にツイートする
    with Path(list_path).open("r",encoding="utf-8") as f:
        count = 0
        if Path("engine/count.dat").exists():
          with Path("engine/count.dat").open("r",encoding="utf-8") as c:
                count = int(c.readline())
        lines = f.readlines()
        if len(lines) <= count:
            count = 0
        text = lines[count][0:-1]
    with Path("engine/count.dat").open("w",encoding="utf-8") as c:
                c.write("{0}".format(count+1))
    # Tweet    
    api.update_status(text)
    return
    

if __name__=="__main__":
    main()