# Open CVでできることを調べてみた

### 参考になるページ
##### [画像処理ライブラリ OpenCV で 出来ること・出来ないこと](https://www.slideshare.net/FukushimaNorishige/opencv-67214568)  

##### [機械学習のためのOpenCV入門](http://qiita.com/icoxfog417/items/53e61496ad980c41a08e)  
1. OpenCV Algorithm Module Overview

1. 前処理(閾値処理,フィルター処理(ぼかし))

1. グレースケール化
 ※最終的に機械学習で使用する際はRGB情報が必要なことが多い

1. 閾値処理
 ※windowsのペイントツールのスポイトで色（RGBとHSV）を調べられる
 ※Ubuntuではpinta
インストール
$ sudo apt-get install pinta

1. 平滑化(スムージング)
GaussianBlur
モルフォロジー(Dilation, Erosion, Opening Closing)  

1. 物体検出  
cv2.findContours

1. 輪郭の近似

1. 物体認識

##### [OpenCVでカメラ画像から自己位置認識 (Visual Odometry)](https://blog.negativemind.com/2016/02/19/monocular-visual-odometry-using-opencv/)

##### [Visual SLAM (with OpenCV)](https://chalmersphyscomp10.wordpress.com/2010/09/26/visual-slam-with-opencv/)

### キーワード
1. Point Cloud
1. Features VSLAM
1. Object recognations
