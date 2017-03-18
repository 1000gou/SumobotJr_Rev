## Windows10セッティング
#### ソフト①（RaspbianをマイクロSDカードへの書き込み)
Win32_Disk_Imager   
※ちなみに、Win32_Disk_ImagerでUbuntuインストーラー(*.iso)をUSBメモリへ書き込むこともできました。
#### ソフト②（SSH接続）
Tera Term
※ホスト名(*.local)でアクセスするためにはAppleのbonjour(iTunesをインストールすると勝手にインストールされる)というソフトが必要。

#### ソフト③（SFTP接続）
WinSCP

#### ソフト④（VNC接続）
RealVNC(インストールはViewerだけでよい)

## 勉強会とは関係ないけどWindows10へインストールしたソフト
#### Anaconda
OpenCV on Python on Windows10を実行するために、[Anacondaのサイト](https://www.continuum.io/)からwindows用のインストーラーをダウンロードして実行。   

#### OpneCV3
Anacondaインストール後、以下のコマンドでインストール  
\>conda install --channel https://conda.anaconda.org/menpo opencv3  
※Python3ではOpenCVがうまくインストールできないかったのでとりあえずPython 2.7で実行している。

#### Atom
このメモ（マークダウンファイル *.md)の編集のためにインストール。とても使いやすい。

#### GitKraken  
このメモをGitHubへアップアップロードするためにインストール。  
(Ubuntuでも使えるそうなので、このソフトにしたが、Atomで直接アップロードできそうなのでもう使わないかも。)

## その他
同一ネットワークにつながっているPC等のIPアドレスを見る。  
\>arp -a
