#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import os

def make_window_from_usb_camera():
    cascade_path = "haarcascade_frontalface_alt.xml"

    #カスケード分類器の特徴量を取得する
    cascade = cv2.CascadeClassifier(cascade_path)

    # カメラからキャプチャー
    capture = cv2.VideoCapture(0)
    if capture.isOpened() is False:
        raise("IO Error")

    cv2.namedWindow("USB Camera", cv2.WINDOW_NORMAL)

    while(True):
        # 動画ストリームからフレームを取得
        ret, image = capture.read()
        if ret == False:
            continue

        #物体認識（顔認識）の実行
        color = (255, 255, 255)
        facerect = cascade.detectMultiScale(image, scaleFactor=1.2, minNeighbors=2, minSize=(10, 10))

        for rect in facerect:
            #検出した顔を囲む矩形の作成
            cv2.rectangle(image, tuple(rect[0:2]),tuple(rect[0:2] + rect[2:4]), color, thickness=2)

         # 表示
        cv2.imshow("USB Camera", image)

        #If ESC is pushed this program is finished
        k =  cv2.waitKey(100)
        if  k >= 0:
            print(k)
            break

    capture.release()
    cv2.destroyAllWindows()

    for i in range (1,5):
        cv2.waitKey(1)       #少し待たないとウィンドウがクローズされない

if __name__ == '__main__':
    make_window_from_usb_camera()
