## Ubuntuのセッティング

### Ubuntuのダウンロード
UbuntuのIOSイメージを[ここ](https://www.ubuntulinux.jp/News/ubuntu1404-ja-remix)からダウンロード。  
今回は、ROSを使用するのでUbuntu 14.04LTS(Trusty Tahr)を選択した。

### ブータブルUSBを作成(isoファイルをUSBメモリに焼く)
Windows　:　ダウンロードしたISOイメージ(*.ios)をWin32DiskImagerでUSBに書き込み  
Ubuntu　：　まだやり方わからない。

### Ubuntuのインストール
今回は、ルート（/）およびスワップ領域を外付けSSDのパーティションにインストールした。※スワップ領域の目安は内蔵メモリーの２倍  
(外付けハードディスクがないとウィンドウズも起動できなくなってしまったが誤って内蔵ハードディスクにブートローダをインストールしてしまった？)

### アプリケーションリストとインストールされているアプリケーションのアップデート
$sudo apt-get update  
$sudo apt-get upgrade

### ホームディレクトリの中のディレクトリ名を英語にする
$ LANG=C xdg-user-dirs-gtk-update

### LXDE（軽量デスクトップ）のインストール
$sudo apt-get install lxde

再起動後  LXDEタスクバーを以下のように設定  
音量コントール（追加)、CPU温度（追加) 、スクリーンロック（削除）  
デジタル時計のフォーマット（%Y年%m月%d日%A%R）  
※LXDEのシャットダウンボタンはものすごく遅いので終了するときは ```$sudo halt -p```

### マウスがつながっている時にタッチパッドを無効化する。
$sudo add-apt-repository ppa:atareao/atareao  
$sudo apt-get update  
$sudo apt-get install touchpad-indicator  
このアプリケーションの起動方法がわからなかったのですが、LXDEでは再起動後、スタートボタン→アクセサリの中にタッチパッド・インディケーターのアイコンがあったので、このアイコンで起動するとタスクバーにアイコンが出来ました。その後は、  『設定→動作→マウス接続じはタッチパッドを無効にする 』 『一般的なオプション→自動起動』

### バッテリーモニターのインストール
$sudo add-apt-repository ppa:maateen/battery-monitor   
$sudo apt update  
$sudo apt install battery-monitor  
LXDEのパネルに追加　　

### Terminator（端末）のインストール
$sudo apt-get install terminator  
（FontはUbuntu mono の　Reguler 11が見やすい）  
(Show titlebarのチェックを外す)

### ターミナルのFull Pathの表示をやめる
~/.bashrcの以下の文の小文字のwを大文字のWにする  
変更前　```PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '```  
変更後　```PS1='${debian_chroot:+($debian_chroot)}\u@\h:\W\$ '```  

変更を反映させる   
$source ~/.bashrc もしくは　再起動  

### Google chromのインストール
$sudo wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -  
$sudo sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'  
$sudo apt-get update
$sudo apt-get install google-chrome-stable

### Openssh (SSHサーバー)のインストール
$sudo apt-get install openssh-server

### Avahi (ホスト名でアクセスできるようにする)のインストール
$sudo apt-get install avahi-demon

### Tightvncserver (VNCサーバー)のインストールと設定
VNCサーバのインストール  
$sudo apt-get install tightvncserver  

VNCのpasswordの設定
$vncpasswd

~/.vnc/xstartupを作成(VNCサーバーを一度起動する)  
$vncserver :1 -geometry 1366x768

VNCサーバーを一度止める  
$vncserver -kill :1

~/.vnc/xstartupファイルの修正(LXDE用)  
$nano  ~/.vnc/xstartupで、最後に以下の２行を追加する。  
lxterminal &  
/usr/bin/lxsession -s LXDE &  

VNCサーバーの起動  
$vncserver :1 -geometry 1366x768

### RealVNC connect(この中からViewerのみインストール)
[ここ](https://www.realvnc.com/download/vnc/)からDEB x64
$cd Downloads  
$tar zxvf VNC-6.0.2-Linux-x64-DEB.tar.gz  
$sudo dpkg -i VNC-Viewer-6.0.2-Linux-x64.deb  
$rm *deb

### Python, Python3
最初からインストールされていた。

### Idle, Idle3,Spyder, Spyder3のインストール
$sudo apt-get install Idle  
$sudo apt-get install Idle3  
$sudo apt-get install spyder  
$sudo apt-get install spyder3

### Atomのインストール
$sudo add-apt-repository ppa:webupd8team/atom  
$sudo apt-get update  
$sudo apt-get install atom  

### GitKrakenのインストール
[公式サイト](https://www.gitkraken.com/)よりDebパッケージをダウンロード  
$cd ~/Download  
$sudo gdebi gitkraken-amd64.deb  
$rm gitkraken-amd64.deb

### Fritzing (電気回路を書くソフト)
$sudo add-apt-repository ppa:ehbello/fritzing  
$sudo apt-get update  
$sudo apt-get install fritzing

### FileZiila (SFTPクライアント)

### Open Jtake
#### インストール
$ sudo apt-get install open-jtalk  
$ sudo apt-get install open-jtalk-mecab-naist-jdic hts-voice-nitech-jp-atr503-m001

### ゲームパッド（speed link sl-650000-BK）のインストール
$ sudo apt-get install joystick jstest-gtk
(システムツール → jstest-gtk)

### ヘッドセットのインストール
※使用したヘッドセット：Logicool製ですが、型番は不明です。
※いろいろ試したけどUbuntu 14.04LTS + USBヘッドセット　+ Julius rev.4.3.1の組み合わせでは、1度は起動できるけど、2度目の起動前はUSBを抜き差ししないといけないという不具合ではまり、解決できませんでした。[こちらの方](http://engetu21.hatenablog.com/entry/2014/11/16/155927)も同じ現象が起きているので、そういうものだと思って諦めました。

#### USB機器として認識されているか確認する  
$lsusb  
私の環境では問題なく認識されていました。

#### USBヘッドセットの優先順位の確認
$cat /proc/asound/modules  
 0 snd_hda_intel  
 1 snd_hda_intel  
 2 snd_usb_audio  

#### USBヘッドセットの優先順位の変更
$sudo nano /etc/modprobe.d/alsa-base.conf  

\# Keep snd-usb-audio from beeing loaded as first soundcard     
options snd-usb-audio index=-2  

の行を以下に書き換える

\# Keep snd-usb-audio from beeing loaded as first soundcard  
options snd-usb-audio index=0

#### 再起動してUSBヘッドセットの優先順位の確認
$sudo reboot  
$cat /proc/asound/modules  
0 snd_usb_audio  
1 snd_hda_intel  
2 snd_hda_intel

### ノートPC内蔵スピーカーと内臓マイクを使えるようにする
#### 必要なソフトをインストールする
$ sudo apt-get update  
$ sudo apt-get upgrade  
$ sudo apt-get install alsa-utils sox libsox-fmt-all  
$ sudo apt-get install pavucontrol  

#### マイク（プラグインと内臓）のCard No と Device Noを調べる
$ arecord -l  

#### alsamixerでマイク音量（プラグインと内臓）を設定する
$ alsamixer
F6(サウンドカード選択)→HDA Intel PCH
Auto-Muto : Disable
その他をすべて１００にしてESCで終了

#### alsamixerでマイク音量（プラグインor内臓）を１００に設定する
$ pavucontrol  
入力タブの音量設定を１００にする

#### 録音してみる
$ arecord -D plughw:2,0 -r 16000 -f S16_LE test.wav  
※2,0 はカード番号の2とデバイス番号の0  
※16000はJulius用に16kHz  
※終了はctl+c  

#### 再生してみる
$ aplay test.wav
