# coding : utf-8
from pathlib import Path
import urllib , re

#my-lib
import GetTweetsObject

def main():
    # """
    get_tweets = GetTweetsObject.GetTweetsObject("tweets/OAuth.json")
    get_tweets.get_tweets("CountryError404",exclude_replies=False,avoid_api_regulation=True)
    # """
    
    #デバッグ用処理
    # import dill
    """
    with open("tweets/tweets_ex.pickle","wb") as f:
        dill.dump(get_tweets,f)
    # """
    """
    with open("tweets/tweets_ex.pickle","rb") as f:
        get_tweets = dill.load(f)
    # """

    #MAKEBOTのツイートリストを読む
    with Path("tweets/id_list.txt").open("r") as f:
        regs = f.readlines()
    ids = []
    for reg in regs:
        ids.append(int(reg[43:-1]))

    countries = []
    
    for tweet in get_tweets.tweets:
        #ツイートが登録されていているか。
        if tweet.id in ids:
            if len([c for c in countries if c.main_id == tweet.id]) == 0:
                country = Country(tweet.id,get_display_text(tweet))
                country.media_urls = get_media_urls(tweet)
                j = 0
                for i in ids:
                    if tweet.id == i:
                        country.index = j
                        break
                    j = j + 1
                countries.append(country)
        
        #ツイートが登録されたもののリプライか。
        if tweet.in_reply_to_status_id in ids:
            if len([c for c in countries if c.main_id == tweet.in_reply_to_status_id]) == 0:
                parent = [ t for t in get_tweets.tweets if t.id == tweet.in_reply_to_status_id][0]
                country = Country(parent.id,get_display_text(parent))
                country.media_urls = get_media_urls(parent)
                j = 0
                for i in ids:
                    if parent.id == i:
                        country.index = j
                        break
                    j = j + 1
                countries.append(country)
            country = [c for c in countries if c.main_id == tweet.in_reply_to_status_id][0]
            country.reply_id = tweet.id
            country.reply_text = get_display_text(tweet)

    for c in countries:
        d = Path("tweets") / Path("{0}_{1}".format(c.index,
        c.name.replace(" ","").replace(":","_").replace("/","_")))
        print(c.name)
        d.mkdir()
        with (d / Path("main.txt")).open("w",encoding="utf-8") as f:
            f.writelines("ID: {0}\n\n".format(c.main_id))
            f.writelines(c.main_text)
        with (d / Path("reply.txt")).open("w",encoding="utf-8") as f:
            f.writelines("ID: {0}\n\n".format(c.reply_id))
            f.writelines(c.reply_text)

        # メディア取得
        i = 0
        for u in c.media_urls:
            try:
                with urllib.request.urlopen(u) as raw:
                    img = raw.read()
                    # 拡張子決める
                    ex = re.findall(r"\.[A-Z,a-z,0-9]*",u,)[-1]
                    with (d / Path("{0}{1}".format(i,ex))).open("wb") as f:
                        f.write(img)
                    i = i + 1
            except:
                print("ERROR! Target:{0} ({1})".format(u,c.name))

def get_media_urls(tweet):
    urls = []
    try:
        for e in tweet.extended_entities["media"]:
            urls.append(e["media_url"])
    finally:
        return urls        

def get_display_text(tweet):
    s , e = tuple(tweet.display_text_range)
    return tweet.full_text[s:e]

class Country:
    def __init__(self,mmain_id,main_text=""):
        self.main_text = main_text
        self.main_id = mmain_id
        self.name = str(re.search(r"\A【.*】",self.main_text).group(0))[1:-1]
        
if __name__=="__main__":
    main()
