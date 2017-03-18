#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webiopi
import sys
import cv2
import numpy as np
import time

GPIO = webiopi.GPIO

PIN_RIGHT = 13  #GPIOピンNo 右車輪
PIN_LEFT = 12   #GPIOピンNo 左車輪

image_size_x= 640

"""イニシャライズ"""
def setup():
  #車輪用サーボをPWMモードにする
  GPIO.setFunction(PIN_RIGHT, GPIO.PWM)
  GPIO.setFunction(PIN_LEFT, GPIO.PWM)

"""終了処理"""
def destroy():
  #PWMを0にしてから、インプットモードにしておく
  GPIO.pulseMicro(PIN_RIGHT, 0, 2000)
  #GPIO.setFunction(PIN_RIGHT, GPIO.INPUT)
  GPIO.pulseMicro(PIN_LEFT, 0, 2000)
  #GPIO.setFunction(PIN_LEFT, GPIO.INPUT)

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

"""Move"""
def Move(direction):
  if direction > image_size_x/2+40:
    turn_right()
    s = abs(direction-  image_size_x/2)/(image_size_x/2)*0.001
    print("Turn right : " + str(s) + " s")
    time.sleep(s)
    stop()
  elif direction < image_size_x/2-40:
    turn_left()
    s = abs(direction-  image_size_x/2)/(image_size_x/2)*0.001
    print("Turn Left : " + str(s) + " s")
    time.sleep(s)
    stop()
  else:
    forward()
    time.sleep(0.2)
    stop()


def make_window_from_usb_camera():
    capture = cv2.VideoCapture(0)
    for i in range(1,10):
        ret, image = capture.read()
        cv2.waitKey(10)


    if capture.isOpened() is False:
        raise("IO Error")

    #Make windows
    cv2.namedWindow("USB Camera", cv2.WINDOW_AUTOSIZE)
    cv2.namedWindow("Modified Image", cv2.WINDOW_AUTOSIZE)

    while True:
        ret, image = capture.read()
        if ret == False:
            continue
        #Get Image X size
        image_size_x =  image.shape[1]

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
                print("x = "+str(i[0])+"  radius = "+str(i[2]))
                Move(i[0])
        else:
          print("No Circles")
          #turn_right()
          #time.sleep(0.2)
          stop()

        #Describe windows
        cv2.imshow("USB Camera", image)

        cv2.imshow("Modified Image", modified_image)

       #If ESC is pushed this program is finished
        k =  cv2.waitKey(100)
        if  k >= 0:
            print(k)
            break

    #Prepare to finish
    stop()
    destroy()
    cv2.destroyAllWindows()
    #少し待たないとウィンドウがクローズされない
    for i in range (1,10):
        cv2.waitKey(10)

if __name__ == '__main__':
    setup()
    make_window_from_usb_camera()
    print("exit program")
