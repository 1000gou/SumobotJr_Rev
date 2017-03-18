#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import numpy as np

WINDOW_NAME = "Capture"

###########################################################################
#Ball detect クラス
class Ball_detect_Class:
    def __init__(self, size_x, size_y, show_window_flag):
        self.size_x = size_x
        self.size_y = size_y
        self.show_window_flag = show_window_flag

        #Camera device initilization
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH , self.size_x)
        self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.size_y )

        #カメラディバイスが取得出来ない場合はエラーを投げる
        if self.capture.isOpened() is False:
            print('Camera device can not be initialized')
            raise('Camera device initialization error')

        #Windowの作成
        if  self.show_window_flag:
            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)

    def GetImage(self):
        flag, self.image = self.capture.read()
        if flag == True:
            self.UpdateWindow()
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
            lower = np.array([80, 100, 100])
            upper = np.array([130, 255, 255])
            hsv = cv2.cvtColor(self.image,cv2.COLOR_BGR2HSV)
            return cv2.inRange(hsv,lower,upper)

    def Extract_Yellow(self, image):
            # 黄色を検出
            lower = np.array([30, 20, 150])
            upper = np.array([70, 255, 255])
            hsv = cv2.cvtColor(self.image,cv2.COLOR_BGR2HSV)
            return cv2.inRange(hsv,lower,upper)

    def UpdateWindow(self):
        if  self.show_window_flag:
            #self.image =  self.Extract_Red(self.image)
            #self.image =  self.Extract_Yellow(self.image)
            self.image =  self.Extract_Blue(self.image)
            cv2.imshow(WINDOW_NAME, self.image)
            cv2.waitKey(10)

    def Cleanup(self):
        self.capture.release()
        cv2.destroyAllWindows()
        #ラズパイでは少し待たないとウィンドウがクローズされない
        for i in range (1,10):
            cv2.waitKey(100)

if __name__ == '__main__':
    try:
        ball_detect = Ball_detect_Class(240,160, True)    #Image size X= 240, Y = 160, Show window True
        while True:
            ball_detect.GetImage()
    except KeyboardInterrupt  :         #Ctl+Cが押されたらループを終了
        print("\nCtl+C")
    except Exception as e:
        print(str(e))
    finally:
        ball_detect.Cleanup()
        print("\nexit program")
