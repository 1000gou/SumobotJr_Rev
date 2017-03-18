## Smobot Jrでボールの追従
#### ボールを追従している様子
[![](http://img.youtube.com/vi/eoHO4iAvcaQ/0.jpg)](https://www.youtube.com/watch?v=eoHO4iAvcaQ)


#### サンプルプログラム 青いボールの追従([03_sumobot_opencv2_blue_ball.py](03_sumobot_opencv2_blue_ball.py))
※こののサンプルプログラムは、Python2 + OpenCV2で実行する必要があります。  

```Python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import sys
import cv2
import numpy as np

############################################################################
#GWS_35_STDをコントロールするためのクラス
class GWS_S35_STD_Class:
    # mPin : GPIO No (PWM)
    # mPwm : Pwmコントロール用のインスタンス
    # mReversal (1:CW/CCWそのまま、−１:CW/CCW反転)
    """コンストラクタ"""
    def __init__(self, Pin, Reversal):
        self.mPin = Pin
        self.mReversal = Reversal

        #車輪用GPIOをPWMモードにする
        GPIO.setup(self.mPin, GPIO.OUT)
        self.mPwm = GPIO.PWM(self.mPin , 500) # set 2.0ms / 500 Hz
        self.Stop()

    """停止"""
    def Stop(self):
        self.mPwm.start(0)

    """速度セット"""
    def SetSpeed(self, speed):
        if speed > 100:
            speed = 100
        elif speed < -100:
            speed = -100
        elif -10 < speed and speed < 10:
            self.Stop()
        else:
            #Duty ratio = ６０％〜９０％（1.2ms〜1.8ms)
            duty = (self.mReversal*speed+100)/200*30+60
            self.mPwm.start(duty)

    """終了処理"""
    def Cleanup(self):
        #PWMを0にしてから、インプットモードにしておく
        self.Stop()
        GPIO.setup(self.mPin, GPIO.IN)

############################################################################
#SumobotJrをコントロールするためのクラス
class SumobotJr_Class:
    """コンストラクタ"""
    def __init__(self):
        #車輪用DCモーターコントローラーインスタンス作成
        try:
            #Useing GPIO No.  to idetify channel
            GPIO.setmode(GPIO.BCM)
            self.left_servo = GWS_S35_STD_Class(Pin = 12, Reversal=1)       #左車輪用サーボ
            self.right_servo = GWS_S35_STD_Class(Pin = 13, Reversal=-1)     #右車輪用サーボ
            #self.left_servo = GWS_S35_STD_Class(Pin = 17, Reversal=1)       #左車輪用サーボ
            #self.right_servo = GWS_S35_STD_Class(Pin = 27, Reversal=-1)     #右車輪用サーボ
            self.no_problem = True                                          #クラスの中で問題が起きていないか(True:問題なし)
            print("servo motor initialization succeeded")
        except Exception as e:
            self.no_problem = False
            print("DC motor initialaization error")
            print(str(e))

    """停止"""
    def Stop(self):
        self.left_servo.SetSpeed(0)
        self.right_servo.SetSpeed(0)

    """前進"""
    def Forward(self):
        self.left_servo.SetSpeed(100)
        self.right_servo.SetSpeed(100)

    """後退"""
    def Backward(self):
        self.left_servo.SetSpeed(-100)
        self.right_servo.SetSpeed(-100)

    """左折"""
    def Turn_left(self):
        self.left_servo.SetSpeed(-100)
        self.right_servo.SetSpeed(100)

    """右折"""
    def Turn_right(self):
        self.left_servo.SetSpeed(100)
        self.right_servo.SetSpeed(-100)

    """サーボ"""
    def SetSpeed(self, left, right):
        self.left_servo.SetSpeed(left)
        self.right_servo.SetSpeed(right)

    """終了処理"""
    def Cleanup(self):
        self.left_servo.Cleanup()
        self.right_servo.Cleanup()
        GPIO.cleanup()

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
        SumobotJr = SumobotJr_Class()
        ball_detect = Ball_detect_Class(IMAGE_X,IMAGE_X, True, False)
        pre_x_ratio = -50

        while True:
            x_ratio, y_ratio = ball_detect.Get_Blue_Rect_Position_Ratio()
            print("Ratio x:"+str(x_ratio)+"  y:"+str(y_ratio))
            print("Pre_ratio x:"+str(pre_x_ratio))

            if x_ratio == -200:
                #ボールが見つからないとき
                #SumobotJr.Stop()
                if pre_x_ratio < 0:
                    SumobotJr.Turn_left()
                else:
                    SumobotJr.Turn_right()
            elif x_ratio < -50:
                pre_x_ratio = x_ratio
                SumobotJr.SetSpeed(100-abs(x_ratio),100)
            elif x_ratio > 50:
                pre_x_ratio = x_ratio
                SumobotJr.SetSpeed(100,100-abs(x_ratio))
            else:
                SumobotJr.Forward()
    except KeyboardInterrupt  :         #Ctl+Cが押されたらループを終了
        print("\nCtl+C")
    except Exception as e:
        print(str(e))
    finally:
        SumobotJr.Cleanup()
        print("\nexit program")
```
