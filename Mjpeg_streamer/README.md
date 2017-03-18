## USBカメラでストリーミング（MJPG-steamer）
#### USBカメラの動作確認
カメラをとりつけ、$lsusbでカメラが認識されていることを確認
※家にあったUSBカメラ(たぶんHD Webcam C270)はつないだだけで認識されていました。

#### ラズパイ上(HDMI or VNC接続)での映像確認
gucviewをインストール(もしかして最初からインストールされていた？)  
$ sudo apt-get update  
$ sudo apt-get upgrade  
$ sudo apt-get install guvcview

gucviewを実行し映像が見れることを確認する  
$sudo guvcview  

#### MJPG-steamerのインストール
$sudo apt update  
$sudo apt install subversion libjpeg-dev imagemagick  
$svn co https://svn.code.sf.net/p/mjpg-streamer/code/mjpg-streamer mjpg-streamer  
$cd mjpg-streamer   
$make  
$sudo make install  
$sudo usermod -a -G video [ユーザー名]  

####  MJPG-steamerの実行
$sudo /home/pi/mjpg-streamer/mjpg_streamer -i "/home/pi/mjpg-streamer/input_uvc.so -f 10 -r 320x240 -d /dev/video0 -y -n" -o "/home/pi/mjpg-streamer/output_http.so -w /home/pi/mjpg-streamer/www -p 8080"  
※終了はctl+Cまたは$kill -9 'pidof mjpg_streamer'  
※終了後再起動できなくなる時があるが、その時は一度USBコネクタを抜いてさし直すとまた起動できる。

#### MJPG-steamerの動作確認
ブラウザで http://IPアドレス:8080/にアクセスする

#### MJPG-streamerのストリーミングをページへ埋め込むときのタグ
`<img src="http://IPアドレス:8080/?action=stream" width="640" height="480"\>`

#### MJPG-streamerの自動起動
以下のコマンドを/etc/rc.localに追記する  
$sudo /home/pi/mjpg-streamer/mjpg_streamer -i "/home/pi/mjpg-streamer/input_uvc.so -f 10 -r 320x240 -d /dev/video0 -y -n" -o "/home/pi/mjpg-streamer/output_http.so -w /home/pi/mjpg-streamer/www -p 8080"
