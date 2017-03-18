#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2.cv as cv
import cv2
import socket

UBU_HOST_NAME = 'gaubutwo.local'#ラズパイUDP受信ホスト名
UBU_HOST_PORT = 4001            #ラズパイUDP受信ポート番号

if __name__ == "__main__":
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #cv.NamedWindow("ClientCAM", 1)
    capture = cv.CaptureFromCAM(0)#キャプチャに使うカメラの選択
    cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_WIDTH,320)#キャプチャする画像のサイズ
    cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_HEIGHT,240)
    while True:
        img = cv.QueryFrame(capture)#画像のキャプチャ
        jpgstring = cv.EncodeImage(".jpeg", img).tostring()#UDPで送る為に画像をstringに変換
        cv.ShowImage("ClientCAM", img)

        udp.sendto(jpgstring, (UBU_HOST_NAME, UBU_HOST_PORT))#画像の送信
        if cv.WaitKey(10) == 27:
            break #エスケープキー（だったけ・・・・？）にて終了
    cv.DestroyAllWindows()#事後処理
    udp.close()
