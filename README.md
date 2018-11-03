# CountryError404
地図に載らない国bot(@CountryError404)関連のリポジトリ

# tweets
全記事と記事収集用スクリプト。ボットエンジンに登録しているデータ(id_list.txt)

# engine
Herokuで1時間ごとに呼び出すスクリプト。ルートのrequirements.txtとruntime.txtは依存関係を記述。  
Heroku Scheduler + AmazonS3で動いている。