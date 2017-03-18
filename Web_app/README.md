## Web applicationの例
[情報元](http://fabble.cc/fablabkannai/sumobotxjrxwithxraspberryxpi/note/note_cards/8767)
#### 環境設定
※環境設定の前にPython2でWiringPiが使える必要がある  

$ sudo apt-get update  
$ sudo apt-get install python-dev   
$ sudo pip2 install virtualenv   

SumobotWebSample1 のインストール
$ cd /tmp
$ git clone https://github.com/FabLabKannai/SumobotJr.git
$ mkdir ~/sumobot/
$ mv SumobotJr/raspi/sumobot_web/SumobotWebSample1/ ~/sumobot/

$ virtualenv venv  
※Python3で実行されてしまうけど大丈夫？

$ source venv/bin/activate   
(venv) $ cd ~/sumobot/SumobotWebSample1   
(venv) $ python setup.py install   
(venv) $ deactivate  

$sudo sh init.sh

#### 実行
よくわからないが以下のコマンドで手動で起動する必要あり。  
$sudo python ~/sumobot/SumobotWebSample1/build/lib/sumobot_web_sample_1/\__init__.py

http://ホスト名.local:6010/　へブラウザでアクセスする
