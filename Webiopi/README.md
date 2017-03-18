## ブラウザからラズパイの遠隔操作（WebIOPi）
### ※WebIOPiはPython3のみ対応しているらしい。
#### WebIOPiのインストール
##### ダウンロード
WebIOPi-*.*.*.tar.gzをダウンロード  
windowsでダウンロードした場合はSFTPでラズパイへコピー
##### 解凍
$tar xzvf WebIOPi-0.7.1.tar.gz  
$cd cd WebIOPi-0.7.1/

##### パッチをあてる（必要？)  
$wget https://raw.githubusercontent.com/doublebind/raspi/master/webiopi-pi2bplus.patch  
$patch -p1 -i webiopi-pi2bplus.patch

##### インストール
$sudo ./setup.sh

##### サービスの登録？
$wget https://raw.githubusercontent.com/neuralassembly/raspi/master/webiopi.service  
$sudo mv webiopi.service /etc/systemd/system/

##### サービスの開始
$sudo systemctl start webiopi

##### サービスの終了
$sudo systemctl stop webiopi

##### WebIOPiへの接続
http://IPアドレス:8000/  
デフォルトのユーザー名:webiopi  
デフォルトのパスワード:raspberry

#### サービスの自動起動
自動起動にする $sudo systemctl enable webiopi  
自動起動をやめる $sudo systemctl disable webiopi

#### サンプルではなく自分のプログラムを実行する
/etc/webiopi/configの  
[SCRIPTS]にpythonのスクリプトへのパスを記入(スクリプトは一つしか登録できない？)  
[HTTP]にhtmlのフォルダへのパスを記入

新しいスクリプトへ変更後、一旦サービスを終了  
$sudo systemctl stop webiopi  
デバッグモードで実行  
$sudo webiopi -c /etc/webiopi/config -d  
問題なければサービスを開始  
$sudo systemctl start webiopi  

#### Sumbot サンプルプログラム ([sumobot.py](sumobot.py))
```python
import webiopi
import sys
import subprocess

GPIO = webiopi.GPIO

PIN_RIGHT = 13  #GPIOピンNo 右車輪
PIN_LEFT = 12   #GPIOピンNo 左車輪

"""イニシャライズ"""
def setup():
  #車輪用サーボをPWMモードにする
  GPIO.setFunction(PIN_RIGHT, GPIO.PWM)
  GPIO.setFunction(PIN_LEFT, GPIO.PWM)       

"""終了処理"""
def destroy():
  #PWMを0にしてから、インプットモードにしておく
  GPIO.pulseMicro(PIN_RIGHT, 0, 2000)
  GPIO.setFunction(PIN_RIGHT, GPIO.INPUT)
  GPIO.pulseMicro(PIN_LEFT, 0, 2000)
  GPIO.setFunction(PIN_LEFT, GPIO.INPUT)  

"""メインループ"""
def loop():
  webiopi.sleep(1)

"""停止"""
@webiopi.macro
def stop():
  right_up = 0
  left_up = 0
  GPIO.pulseMicro(PIN_RIGHT, right_up, 2000-right_up)
  GPIO.pulseMicro(PIN_LEFT, left_up, 2000-left_up)

"""前進"""
@webiopi.macro
def forward():
  right_up =  1100
  left_up = 1900
  GPIO.pulseMicro(PIN_RIGHT, right_up, 2000-right_up)
  GPIO.pulseMicro(PIN_LEFT, left_up, 2000-left_up)

"""後退"""
@webiopi.macro
def backward():
  right_up =  1900
  left_up = 1100
  GPIO.pulseMicro(PIN_RIGHT, right_up, 2000-right_up)
  GPIO.pulseMicro(PIN_LEFT, left_up, 2000-left_up)

"""右折"""
@webiopi.macro
def turn_right():
  right_up =  1900
  left_up = 1900
  GPIO.pulseMicro(PIN_RIGHT, right_up, 2000-right_up)
  GPIO.pulseMicro(PIN_LEFT, left_up, 2000-left_up)

"""左折"""
@webiopi.macro
def turn_left():
  right_up =  1100
  left_up = 1100
  GPIO.pulseMicro(PIN_RIGHT, right_up, 2000-right_up)
  GPIO.pulseMicro(PIN_LEFT, left_up, 2000-left_up)

"""ラズパイ終了"""
@webiopi.macro
def raspberry_pi_halt():
  cmd = "sudo halt"
  subprocess.call(cmd,  shell=True)

"""mjpg_streamer スタート"""
@webiopi.macro
def mjpg_streamer_start():
  cmd = "sudo /home/pi/mjpg-streamer/mjpg_streamer -i \"/home/pi/mjpg-streamer/input_uvc.so -f 10 -r 320x240 -d /dev/video0 -y -n\" -o \"/home/pi/mjpg-streamer/output_http.so -w /home/pi/mjpg-streamer/www -p 8080\" &"
  subprocess.call(cmd,  shell=True)
```

#### Sumobot html ([sumobot.html](sumobot.html))
```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>WebIOPi | Light Control</title>
    <script type="text/javascript" src="/webiopi.js"></script>
    <script type="text/javascript">
    webiopi().ready(function() {
        var StopButton = webiopi().createButton("StopButton", "とまる", function(){webiopi().callMacro("stop");});
        var ForwardButton = webiopi().createButton("ForwardButton", "ぜんしん", function(){webiopi().callMacro("forward");});
        var BackwardButton = webiopi().createButton("BackwardButton", "こうたい", function(){webiopi().callMacro("backward");});
        var TurnLeftButton = webiopi().createButton("TurnLeftButton", "ひだり", function(){webiopi().callMacro("turn_left");});
        var TurnRightButton = webiopi().createButton("TurnRightButton", "みぎ", function(){webiopi().callMacro("turn_right");});
        var StreamerStartButton = webiopi().createButton("StreamerStartButton", "カメラ", function(){webiopi().callMacro("mjpg_streamer_start");});
        var RaspiHaltButton = webiopi().createButton("RaspiHaltButton", "おわり", function(){webiopi().callMacro("raspberry_pi_halt");});

        // Append button to HTML element with ID="controls" using jQuery
        $("#bStop").append(StopButton);
        $("#bForward").append(ForwardButton);
        $("#bBackward").append(BackwardButton);
        $("#bTurnLeft").append(TurnLeftButton);
        $("#bTurnRgiht").append(TurnRightButton);
        $("#bStreamerStartButton").append(StreamerStartButton);
        $("#bRaspiHaltButton").append(RaspiHaltButton);
    });

    </script>
    <style type="text/css">
        button{
            display: block;
            margin: 5px 5px 5px 5px;
            width: 100px;
            height: 40px;
            font-size: 10pt;
            font-weight: bold;
            color: white;
        }
    </style>
</head>
<body>

<center>
  <img src="http://GApi.local:8080/?action=stream" width="320" height="240">
</center>


<div id="bForward" align="center"></div>
<center><div style="display:inline-flex;">
  <div id="bTurnLeft" class="button1"></div>
  <div id="bStop" class="button1"></div>
  <div id="bTurnRgiht" class="button1"></div>
</div></center>

<div id="bBackward" align="center"></div>

<br><br><br>
<Hr Width="80%">
<div id="bStreamerStartButton" class="button2" align="center"></div>
<Hr Width="80%">
<div id="bRaspiHaltButton" class="button2" align="center"></div>

</body>
</html>
```
