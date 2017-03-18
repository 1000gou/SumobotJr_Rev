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
