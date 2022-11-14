## はじめに
本スクリプトを利用して、自動でamazonのホームページにログインし、レシートをダウンロードすることが可能

## 利用技術・ランタイム
- Python 3.10.0
- selenium 4.6.0

## 実行時の引数指定
|  args  |  説明  |  例  |  デフォルト値  |
| ---- | ---- | ---- | ---- |
|  -c, --count  |  ダウンロードする領収書の件数を指定  |  10, 20, 100  | 10 |
|  -b, --browser  |  chromedriver  | chromedriver,MicrosoftWebDriver.exe   | chromedriver |
| -y, --year  |  ダウンロードする領収書の年を指定  |  2022,2020  |  現在の年  |
|  --headless  |  ヘッドレスモードを利用するかどうか  |  True, False  |  False  |