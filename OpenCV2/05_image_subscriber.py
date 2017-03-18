#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2.cv as cv
import cv2
import numpy
import socket
UBU_HOST_NAME = 'gaubutwo.local'    #ラズパイUDP受信ホスト名
UBU_HOST_PORT = 4001                #ラズパイUDP受信ポート番号
if __name__ == "__main__":
    cv.NamedWindow("serverCAM", 1)  #表示するウィンドウ作成
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(('gaubutwo.local', 4001))
    buff = 1024
    while True:
        jpgstring, addr = udp.recvfrom(buff*64)#送られてくるデータが大きいので一度に受け取るデータ量を大きく設定
        narray = numpy.fromstring(jpgstring, dtype = "uint8")#string型からnumpyを用いuint8に戻す
        decimg = cv2.imdecode(narray,1)#uint8のデータを画像データに戻す
        cv2.imshow("serverCAM", decimg)#画像の表示
        if cv.WaitKey(10) == 27:
            break
    cv.DestroyAllWindows()
    udp.close()
