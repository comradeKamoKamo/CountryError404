#!/usr/bin/env python
import tweepy
import os
from datetime import datetime
from pathlib import Path
import pickle
import boto3

def main():

    #時刻制御
    if datetime.now().hour > 22 or datetime.now().hour < 7:
        exit()

    #S3 Load
    Path("tmp").mkdir(exist_ok=True)
    s3 , bucket =  save_from_s3(s3_name="countryerror404")

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
    follow_and_remove(api)
    tweet_news(api)
    
    #S3 Save
    save_to_s3(s3,bucket)

def save_to_s3(s3,bucket):
    bucket.upload_file('tmp/count.dat', 'count.dat')
    if Path("tmp/protected_users.pickle").exists():
        bucket.upload_file('tmp/protected_users.pickle', 'protected_users.pickle')
    return

def save_from_s3(s3_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(s3_name)
    try:
        bucket.download_file("count.dat", "tmp/count.dat")
        bucket.download_file("protected_users.pickle", "tmp/protected_users.pickle")
    except:
        print("Download from S3 failed.")
    return s3 , bucket
        

def tweet_articles(api,list_path):
    # リストから順番にツイートする
    with Path(list_path).open("r",encoding="utf-8") as f:
        count = 0
        if Path("tmp/count.dat").exists():
          with Path("tmp/count.dat").open("r",encoding="utf-8") as c:
                count = int(c.readline())
        lines = f.readlines()
        if len(lines) <= count:
            count = 0
        text = lines[count][0:-1]
    # Tweet    
    try:
        api.update_status(text)
    except tweepy.TweepError as e:
        if e.api_code==187:
            #ツイートの重複
            count = count + 1
    with Path("tmp/count.dat").open("w",encoding="utf-8") as c:
                c.write("{0}".format(count+1))
    return

def tweet_news(api):
    #単語取得
    keywords = []
    with Path("engine/keywords.txt").open("r",encoding="utf-8") as f:
        for line in f.readlines():
            if line[0:1]=="#" or line[0:1]=="\n":
                continue
            keywords.append(list(line[0:-1].split(","))) 

    #ニュースメディアリストから最新900件を取得。
    for tweet in tweepy.Cursor(api.list_timeline,"CountryError404",
    "Media",tweet_mode="extended").items(900):
        text = get_display_text(tweet)
        retweeted = False
        for wset in keywords:
            if wset[0] in text:
                if len(wset) > 1:
                    for i in range(1,len(wset)-1):
                        if wset[i] in text:
                            if not tweet.retweeted:
                                api.retweet(tweet.id)
                                retweeted = True
                                print(text)
                            break
                else:
                    if not tweet.retweeted:
                        api.retweet(tweet.id)
                        retweeted = True
                        print(text)
            if retweeted: break
        
def get_display_text(tweet):
    s , e = tuple(tweet.display_text_range)
    return tweet.full_text[s:e]

def follow_and_remove(api):
    #24時間で1000回まで。1時間100回。
    users = []
    protected_users = []
    followers_id = []
    for follower_id in tweepy.Cursor(api.followers_ids).items():
        followers_id.append(follower_id)
    friends_id = []
    for friend_id in tweepy.Cursor(api.friends_ids).items():
        friends_id.append(friend_id)

    if len(followers_id) > 0:    
        if Path("tmp/protected_users.pickle").exists():
            with Path("tmp/protected_users.pickle").open("rb") as f:
                protected_users = pickle.load(f)
        #LOOKUPで100ごと取得
        for i in range(0, len(followers_id), 100):
            for follower in api.lookup_users(user_ids=followers_id[i:i+100]):
                if not follower.following:
                    if follower.protected:
                        #鍵垢の場合は1回だけフォローリクエストを送る。
                        if not follower.id in protected_users:
                            if not follower.follow_request_sent:
                                users.append(follower)
                                protected_users.append(follower.id)     
                    else:
                        users.append(follower)
        for i in range(100):
            if len(users) <= i:
                break
            users.pop().follow()

        #鍵垢リストの確認
        for user_id in protected_users:
            #フォロー外されている
            if not user_id in followers_id:
                protected_users.remove(user_id)
            #フォローしている
            try:
                if api.get_user(user_id).following:
                    protected_users.remove(user_id)
            except tweepy.TweepError:
                # tweepy.error.TweepError: [{'code': 50, 'message': 'User not found.'}]
                    protected_users.remove(user_id)
        #鍵垢リスト保存
        with Path("tmp/protected_users.pickle").open("wb") as f:
            pickle.dump(protected_users,f)

    #リムーブ
    removers_id = []
    for friend_id in friends_id:
        if not friend_id in followers_id:
            removers_id.append(friend_id)
    for i in range(100):
        if len(removers_id) <= i:
            break
        api.destroy_friendship(removers_id.pop())
    


if __name__=="__main__":
    main()