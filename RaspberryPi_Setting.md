## ラズパイのセッティング
#### 外部PC(Windows10等)からアクセスできるようにする。
①モニター、キーボード、マウスを接続して、起動。  
②メニュー→設定→Raspberry Piの設定→インターフェースから、SSH, VNC, シリアルを有効にする。  
③メニュー→設定→Raspberry Piの設定→ ローカライゼーションからjapanを選択するとwifiが有効になったので、SSIDとパスワードを入力すれば、Wifiがつながる。

#### ホスト名でアクセスできるようにする。
avahiをインストールした？ or 最初からインストールされていた？  
ホスト名でつながらないときは、Windowsでarp -aコマンドで接続されているコンピュータのIPアドレス一覧から、ラズパイのIPを勘で探す。外出先でつなぐ人はラズパイのMACアドレスをメモっておくとよいかも。

#### シリアル接続（ラズパイ）
①USBシリアル変換ケーブルでWindows PCとRaspberry piを接続。  
(接続するピン配列はググると写真がいっぱい出てきます。）  
②WindowsのTera Termでボーレートを115200にして接続する。  
  ※接続後エンターを押さないとなにも反応しないないように見えるので注意。

#### SSH接続(LANケーブル直結)
私の環境では、PCとラズパイをLANケーブル（ストレートでもよい）でつないでWindowsのTera Termでアクセスする。私の環境では、ラズパイのIPアドレスなぜかいつも169.254.42.87になっている。

#### SSH接続(Wifi)
基本的にSSH(LANケーブル接続と同じ)

#### SFTP接続
ラズパイ側はSSHがつながれば特に設定することはなし。
WindowsからWinSCPで接続出来た。

#### VNC接続(リモートデスクトップ)
ラズパイ側は、メニュー→設定→Raspberry Piの設定→インターフェースから、VNCを有効にするだけでよい。  
Windows側はRealVNCをインストール(Viewerだけでよい)  
File->New connection -. VNT Server に「ホスト名.local:5900」で接続。

## 勉強会とは関係ないけど試してみたこと
#### Python
ラズパイにはPython2と3が最初から両方ともインストールされている。  
$Python -V : Python2のバージョン確認  
$Python3 -V: Python3のバージョン確認  
※idle,pip,spyderも同じ(\*でPython2, \*3でpython3)  

#### idle (Python用IDE？、ただしSpyderの方が使いやすかった)
Python2で起動　$ sudo idle &  
Python3で起動　$ sudo idle3 &  
UTF-8にする　option -> Default Source Encoding をUTF-8を選択  
行番号が表示できないのでエラーが起きたときは　Edit -> Go to line (alt G)　を使う。  
プログラムの実行　RUN→RUN Module (F5)

###### デバッガの使いかた  
エディタを右クリックでブレークポイントの追加と削除  
ブレークポイントを有効にするにはシェルのDebug->Debuggerからデバッグウィンドウを表示してから実行->outを押すとブレークポイントまで実行される

#### PHP
$sudo apt-get install php5 でインストールしたが使っていない。

#### Apache
インストール  
$sudo apt-get install apache2  
※http://ipアドレス/ は /var/www/html/index.html

## その他メモ
ラズパイのピン配列は[ここ](http://www.atmarkit.co.jp/ait/articles/1511/18/news043.html)にあるのが見やすい。
