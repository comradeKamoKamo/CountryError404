# CountryError404
地図に載らない国bot(@CountryError404)関連のリポジトリです。各フォルダについて説明します。  
このbotは主にPython 3によって記述された自作スクリプトで動作しています。

# docs
[GitHub Pages](https://comradekamokamo.github.io/CountryError404/)のデータが配置されます。

# tweets
全記事バックアップと記事収集用スクリプト。ボットエンジンに登録しているデータ(id_list.txt)

# engine
Herokuで1時間ごとに呼び出すスクリプト。ルートのrequirements.txtとruntime.txtは依存関係を記述。  
keywords.txtはニュースをリツイートする際の単語リストです。  
Heroku + Heroku Scheduler + AmazonS3で動いている。(deployブランチがデプロイされます)