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
