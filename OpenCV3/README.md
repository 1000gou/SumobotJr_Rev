## Open CV3トライアル

#### Open CV 3.1.0をコンパイルしてからインストール(python3でも使える）
[参考にしたページ](http://tomosoft.jp/design/?p=7476)

$ sudo apt-get install build-essential cmake pkg-config  
$ sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev  
$ sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev  
$ sudo apt-get install libxvidcore-dev libx264-dev  
$ sudo apt-get install libgtk2.0-dev  
$ sudo apt-get install libatlas-base-dev gfortran  
$ cd ~  
$ wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.1.0.zip  
$ unzip opencv.zip  
$ wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.1.0.zip  
$ unzip opencv_contrib.zip  
$ cd ~/opencv-3.1.0/  
$ mkdir build  
$ cd build  
$ cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D INSTALL_PYTHON_EXAMPLES=ON -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.1.0/modules -D BUILD_EXAMPLES=ON ..  
$ make -j4  
		※ここで、90分くらいかかる  
$ sudo make install  
$ sudo ldconfig

#### OpenCVのバージョン確認
$ python3  
\>>> import cv2   
\>>> cv2.\__version__  
※OpenCV2 用 OpenCV3でコードが微妙に異なるので、必ずサンプルコードを動かす前にバージョンを確認すること

#### usbカメラから画像を取得しjpgで保存する ([11_opencv3.py](11_opencv3.py))
```Python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# OpenCVをインポート
import cv2

def get_image_from_usb_camera():
    # カメラデバイスを取得
    c = cv2.VideoCapture(0)
    # readで画像をキャプチャ、imgにRGBのデータが入ってくる
    r, img = c.read()
    # 保存
    cv2.imwrite('test1.jpg', img)

if __name__ == '__main__':
    get_image_from_usb_camera()
```
#### ウィンドウにカメラからの画像を表示する ([12_opencv3.py](12_opencv3.py))
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2

def make_window_from_usb_camera():
    capture = cv2.VideoCapture(0)
    if capture.isOpened() is False:
        raise("IO Error")

    #cv2.namedWindow("Capture", cv2.CV_WINDOW_AUTOSIZE)
    cv2.namedWindow("Capture", cv2.WINDOW_NORMAL)

    while True:
        ret, image = capture.read()
        if ret == False:
            continue

        cv2.imshow("Capture", image)

        #If ESC is pushed this program is finished
        k =  cv2.waitKey(100)
        if  k >= 0:
            print(k)
            #cv2.imwrite("test1.png", image)
            break

    cv2.destroyAllWindows()
    #少し待たないとウィンドウがクローズされない
    for i in range (1,5):
        cv2.waitKey(1)       

if __name__ == '__main__':
    make_window_from_usb_camera()
```

#### USBカメラの画像から円の検出 ([14_opencv3.py](14_opencv3.py))
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np

def make_window_from_usb_camera():
    capture = cv2.VideoCapture(0)
    if capture.isOpened() is False:
        raise("IO Error")

    cv2.namedWindow("USB Camera", cv2.WINDOW_NORMAL)

    while True:
        ret, image = capture.read()
        if ret == False:
            continue

        # グレースケール化
        modified_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        modified_image = cv2.GaussianBlur(modified_image , (33, 33), 1)

        # 円検出
        circles = cv2.HoughCircles(modified_image, cv2.HOUGH_GRADIENT, 1, 60, param1=10, param2=85, minRadius=80, maxRadius=200)

        if circles != None:
            print("Circles are found")
            circles = np.uint16(np.around(circles))
            for i in circles[0,:]:
                # 囲み線を描く
                cv2.circle(image,(i[0],i[1]),i[2],(255,255,0),2)
                # 中心点を描く
                cv2.circle(image,(i[0],i[1]),2,(0,0,255),3)

        cv2.imshow("USB Camera", image)

       #If ESC is pushed this program is finished
        k =  cv2.waitKey(100)
        if  k >= 0:
            print(k)
            break

    #Prepare to finish   
    cv2.destroyAllWindows()
    for i in range (1,5):
        cv2.waitKey(1)       #少し待たないとウィンドウがクローズされない cv2.waitKey(0)
    print("exit program")

if __name__ == '__main__':
    make_window_from_usb_camera()
```

#### USBカメラの画像から顔の検出  ([15_opencv3.py](15_opencv3.py))
※同じフォルダに([haarcascade_frontalface_alt.xml](haarcascade_frontalface_alt.xml))を保存すること

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np

def make_window_from_usb_camera():
    capture = cv2.VideoCapture(0)
    if capture.isOpened() is False:
        raise("IO Error")

    cv2.namedWindow("USB Camera", cv2.WINDOW_NORMAL)
    cv2.namedWindow("modified_image", cv2.WINDOW_NORMAL)

    while True:
        ret, image = capture.read()
        if ret == False:
            continue

        #HSVに変換して青を抽出する
        modified_image = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        #low_color = np.array([100, 75, 75])
        #upper_color = np.array([140, 255, 255])

        # 黄色を検出
        lower = np.array([20, 50, 50])
        upper = np.array([100, 255, 255])

        #青色の検出
        #lower = np.array([95, 0, 20])
        #upper = np.array([130, 235, 255])


        modified_image = cv2.inRange(modified_image,lower,upper)
        modified_image = cv2.erode(modified_image, None, iterations=2)
        modified_image = cv2.dilate(modified_image, None, iterations=2)
        modified_image = cv2.GaussianBlur(modified_image , (33, 33), 3)
        cv2.imshow("modified_image", modified_image)


        # 円検出
        circles = cv2.HoughCircles(modified_image, cv2.HOUGH_GRADIENT,
                                   dp=1, minDist=100, param1=40, param2=40,
                                   minRadius=10, maxRadius=300)

        if circles != None:
            print("Circles are found")
            circles = np.uint16(np.around(circles))
            for i in circles[0,:]:
                # 囲み線を描く
                cv2.circle(image,(i[0],i[1]),i[2],(255,255,0),2)
                # 中心点を描く
                cv2.circle(image,(i[0],i[1]),2,(0,0,255),3)

        cv2.imshow("USB Camera", image)

       #If ESC is pushed this program is finished
        k =  cv2.waitKey(100)
        if  k >= 0:
            print(k)
            break

    #Prepare to finish   
    cv2.destroyAllWindows()
    #少し待たないとウィンドウがクローズされない
    for i in range (1,10):
        cv2.waitKey(10)       
    print("exit program")

if __name__ == '__main__':
    make_window_from_usb_camera()
```

#### USBカメラの画像から黄色いボールの検出  ([17_opencv3.py](17_opencv3.py))
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np

def make_window_from_usb_camera():
    capture = cv2.VideoCapture(0)
    if capture.isOpened() is False:
        raise("IO Error")

    cv2.namedWindow("USB Camera", cv2.WINDOW_NORMAL)
    cv2.namedWindow("modified_image", cv2.WINDOW_NORMAL)

    while True:
        ret, image = capture.read()
        if ret == False:
            continue

        #HSVに変換して青を抽出する
        modified_image = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        #low_color = np.array([100, 75, 75])
        #upper_color = np.array([140, 255, 255])

        # 黄色を検出
        lower = np.array([20, 50, 50])
        upper = np.array([100, 255, 255])

        #青色の検出
        #lower = np.array([95, 0, 20])
        #upper = np.array([130, 235, 255])


        modified_image = cv2.inRange(modified_image,lower,upper)
        modified_image = cv2.erode(modified_image, None, iterations=2)
        modified_image = cv2.dilate(modified_image, None, iterations=2)
        modified_image = cv2.GaussianBlur(modified_image , (33, 33), 3)
        cv2.imshow("modified_image", modified_image)


        # 円検出
        circles = cv2.HoughCircles(modified_image, cv2.HOUGH_GRADIENT,
                                   dp=1, minDist=100, param1=40, param2=40,
                                   minRadius=10, maxRadius=300)

        if circles != None:
            print("Circles are found")
            circles = np.uint16(np.around(circles))
            for i in circles[0,:]:
                # 囲み線を描く
                cv2.circle(image,(i[0],i[1]),i[2],(255,255,0),2)
                # 中心点を描く
                cv2.circle(image,(i[0],i[1]),2,(0,0,255),3)

        cv2.imshow("USB Camera", image)

       #If ESC is pushed this program is finished
        k =  cv2.waitKey(100)
        if  k >= 0:
            print(k)
            break

    #Prepare to finish   
    cv2.destroyAllWindows()
    #少し待たないとウィンドウがクローズされない
    for i in range (1,10):
        cv2.waitKey(10)       
    print("exit program")

if __name__ == '__main__':
    make_window_from_usb_camera()
```
