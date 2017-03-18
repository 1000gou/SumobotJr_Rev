## Open CV2トライアル

#### Open CVのインストール(この方法ではpython2では使えるがpython3ではopencvは使えない)
$sudo apt-get update  
$sudo apt-get install libopencv-dev  
$sudo apt-get install python-opencv

#### OpenCVのバージョン確認
$ python  
\>>> import cv2   
\>>> cv2.\__version__  
※OpenCV2 用 OpenCV3でコードが微妙に異なるので、必ずサンプルコードを動かす前にバージョンを確認すること

#### USBカメラから画像を取得しjpgで保存する([01_opencv2.py](01_opencv2.py))
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

#### USBカメラから画像を取得しウィンドウを表示する([02_opencv2.py](02_opencv2.py))
```Python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2

def make_window_from_usb_camera():
    capture = cv2.VideoCapture(0)
    if capture.isOpened() is False:
        raise("IO Error")

    cv2.namedWindow("Capture", cv2.WINDOW_AUTOSIZE)

    while True:
        ret, image = capture.read()
        if ret == False:
            continue

        cv2.imshow("Capture", image)

        #If ESC is pushed this program is finished
        k =  cv2.waitKey(100)
        if  k >= 0:
            break

    cv2.destroyAllWindows()

    #ラズパイでは少し待たないとウィンドウがクローズされない
    for i in range (1,5):
        cv2.waitKey(1)       

if __name__ == '__main__':
    make_window_from_usb_camera()
```
#### USBカメラから画像を取得し青い物を表示する([04_blue_rect_cv2_py2.py](04_blue_rect_cv2_py2.py))
※赤、青、黄色と３色で試したが、屋内では青い物体が最も誤検出しずらかった。

```Python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import numpy as np

###########################################################################
#Ball detect クラス
MAIN_WINDOW_NAME = "Image from Camera"
SUB_WINDOW_NAME = "Modified Image"
IMAGE_X = 240   #カメラから取得する画像のX
IMAGE_Y = 160   #カメラから取得する画像のX
WAIT_TIME = 10  #ウィンドウ更新後の待ち時間ms

class Ball_detect_Class:
    def __init__(self, size_x, size_y, flag_show_main_window, flag_show_sub_window):
        self.size_x = size_x
        self.size_y = size_y
        self.flag_show_main_window = flag_show_main_window
        self.flag_show_sub_window = flag_show_sub_window

        #Camera device initilization
        self.capture = cv2.VideoCapture(0)
        #Set target image size
        self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH , self.size_x)
        self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.size_y )
        #Get actual image size
        self.size_x = self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH )
        self.size_y =  self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

        #カメラディバイスが取得出来ない場合はエラーを投げる
        if self.capture.isOpened() is False:
            print('Camera device initialization error')
            raise('Camera device initialization error')
        else:
            print('Camera device initialization succeeded')
            print('Imaze size X:'+str(self.size_x)+'   Y:'+str(self.size_y) )

        #Windowの作成
        if self.flag_show_main_window:
            cv2.namedWindow(MAIN_WINDOW_NAME, cv2.WINDOW_AUTOSIZE)
        if self.flag_show_sub_window:
            cv2.namedWindow(SUB_WINDOW_NAME, cv2.WINDOW_AUTOSIZE)

        #一度だけイメージを読み込む
        flag, self.image = self.capture.read()
        self.mask = self.image
        if flag == False:
            print("Image can not be get from USB camera")

    def GetImage(self):
        flag, self.image = self.capture.read()
        if flag == False:
            print("Image can not be get from USB camera")

    #Hue(色相)→0~180(181～255の範囲は0からの循環に回される)
    #Saturation(彩度)→0~255
    #Value(明度)→0~255
    def Extract_Red(self, image):
            # Redを検出
            lower = np.array([1, 150, 150])
            upper = np.array([10, 255, 255])
            hsv = cv2.cvtColor(self.image,cv2.COLOR_BGR2HSV)
            return cv2.inRange(hsv,lower,upper)

    def Extract_Blue(self, image):
            #青色の検出
            #lower = np.array([80, 100, 100])
            #upper = np.array([130, 255, 255])
            lower = np.array([100, 200, 150])
            upper = np.array([110, 255, 255])
            hsv = cv2.cvtColor(self.image,cv2.COLOR_BGR2HSV)
            return cv2.inRange(hsv,lower,upper)

    def Extract_Yellow(self, image):
            # 黄色を検出
            lower = np.array([30, 20, 150])
            upper = np.array([70, 255, 255])
            hsv = cv2.cvtColor(self.image,cv2.COLOR_BGR2HSV)
            return cv2.inRange(hsv,lower,upper)

    def UpdateWindow(self):
        if self.flag_show_main_window:
            cv2.imshow(MAIN_WINDOW_NAME, self.image)
        if self.flag_show_sub_window:
            cv2.imshow(SUB_WINDOW_NAME, self.mask)
        cv2.waitKey(WAIT_TIME)

    #青い物体の重心を返す
    def Get_Blue_Rect_Position(self):
        self.GetImage()
        #青色を抽出
        self.mask = self.Extract_Blue(self.image)

        #ノイズ除去
        self.mask = cv2.erode(self.mask, None, iterations=2)
        self.mask = cv2.dilate(self.mask, None, iterations=2)
        #self.mask = cv2.GaussianBlur(self.mask , (33, 33), 3)

        #輪郭の取得
        #contours = cv2.findContours(self.mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours, hierarchy = cv2.findContours(self.mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        #cv2.drawContours(self.image,contours,-1,(0,0,255), thickness = 2)

        rects = []
        for contour in contours:
            approx = cv2.convexHull(contour)
            rect = cv2.boundingRect(approx)
            rects.append(np.array(rect))

        if len(rects) > 0:
            rect = max(rects, key=(lambda x: x[2] + x[3]))
            cv2.rectangle(self.image, tuple(rect[0:2]), tuple(rect[0:2] + rect[2:4]), (0, 0, 255), thickness = 2)
            #print(str(rect)+"\n")
            x = (rect[0]+rect[2]/2)
            y = (rect[1]+rect[3]/2)
            cv2.circle(self.image, (x, y), 10, (0, 0, 255), -1)
            #Windowを更新
            self.UpdateWindow()
            return x, y
        else:
            #Windowを更新
            self.UpdateWindow()
            return -1, -1

    def Get_Blue_Rect_Position_Ratio(self):
        #ratio_x : 画像左端-100、中央０、右端100を返す、物がない場合は-200を返す
        #ratio_y * 画面下端-100、中央０、上端100を返す、物がない場合は-200を返す。
        x, y = ball_detect.Get_Blue_Rect_Position()
        if x == -1:
            return -200,-200
        else:
            ratio_x = (float(x*200)/float(self.size_x))-100
            ratio_y = -((float(y*200)/float(self.size_y))-100)
            return ratio_x, ratio_y

    def Cleanup(self):
        self.capture.release()
        cv2.destroyAllWindows()
        #ラズパイでは少し待たないとウィンドウがクローズされない
        for i in range (1,10):
            cv2.waitKey(100)

if __name__ == '__main__':
    try:
        ball_detect = Ball_detect_Class(IMAGE_X,IMAGE_X, True, False)
        while True:
            x,y = ball_detect.Get_Blue_Rect_Position_Ratio()
            print("Ratio x:"+str(x)+"  y:"+str(y))
    except KeyboardInterrupt  :         #Ctl+Cが押されたらループを終了
        print("\nCtl+C")
    except Exception as e:
        print(str(e))
    finally:
        ball_detect.Cleanup()
        print("\nexit program")
```
