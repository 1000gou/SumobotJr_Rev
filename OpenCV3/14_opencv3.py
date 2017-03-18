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
