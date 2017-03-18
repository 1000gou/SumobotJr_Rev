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
