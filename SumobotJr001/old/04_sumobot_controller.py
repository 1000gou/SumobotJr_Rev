#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import socket
import time
import pygame
from pygame.locals import *
import numpy

############################################################################
#通信関連の定数
PI_HOST_NAME = 'gapithree.local'    #ラズパイUDP受信ホスト名
PI_HOST_NAME = '192.168.2.200'    #ラズパイUDP受信ホスト名
PI_HOST_PORT = 4000                 #ラズパイUDP受信ポート番号
UBU_HOST_NAME = 'gaubutwo.local'    #画像UDP受信ホスト名
#UBU_HOST_NAME = '192.168.2.100'    #画像UDP受信ホスト名
UBU_HOST_PORT = 4001                #画像UDP受信ポート番号
UBU_BUFF_SIZE = 1024*64             #画像UDP受信バッファーサイズ
UBU_SOKET_TIMEOUT = 0.01            #画像UDP受信タイムアウトまでの時間[s]



#OpenCV関連の定数
MAIN_WINDOW_NAME = "Image from Raspberry pi"

#メインループ関連の
WAIT_TIME = 10                      #メインループの待ち時間（ms : これを入れないとウィンドウが更新されない）

def main_loop():
    control_mode = 0        #0:青ボール追跡モード, 1:リモートコントロールモード
    main_loop_flag = True   #Trueの間メインループを回す
    cv2.cv.NamedWindow(MAIN_WINDOW_NAME, 1)  #表示するウィンドウ作成
    use_joystick = True      #True ジョイスティックを使う、　False ジョイスティックを使わない or 初期化に失敗した

    #pygameの初期化
    try:
        if use_joystick:
            pygame.joystick.init()
            joys = pygame.joystick.Joystick(0)
            joys.init()
            pygame.init()
            print("pygame initialaization succeeded")
    except Exception as e:
        print("pygame initialaization error\n")
        print(str(e))
        use_joystick = False

    #ソケットの初期化（コントローラー送信）
    try:
        publisher_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("controler publisher　soket initialaization succeeded")
    except Exception as e:
        print("controler publisher　soket initialaization error\n")
        print(str(e))
        main_loop_flag = False

    #ソケットの初期化（画像受信）
    try:
        receiver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiver_sock.bind((UBU_HOST_NAME, UBU_HOST_PORT))
        receiver_sock.settimeout(UBU_SOKET_TIMEOUT)
        print("Image receiver soket initialaization succeeded")
    except Exception as e:
        print("Image receiver soket initialaization error\n")
        print(str(e))
        main_loop_flag = False

    try:
        while main_loop_flag:
            try:
                if use_joystick:
                    for e in pygame.event.get(): # イベントチェック
                        if e.type == pygame.locals.JOYAXISMOTION: # 7
                            left_stick = -100*joys.get_axis(1)
                            right_stick = -100*joys.get_axis(4)
                            message = "left_right_stick:"+str(left_stick)+":"+str(right_stick)
                            publisher_sock.sendto(message, (PI_HOST_NAME , PI_HOST_PORT))
                        elif e.type == pygame.locals.JOYBUTTONDOWN:
                            print(str(e.button)+'番目のボタン')
                            if e.button == 4:
                                control_mode = 0
                                message = "Change_Mode:"+str(control_mode)+":"+str(control_mode)
                                publisher_sock.sendto(message, (PI_HOST_NAME , PI_HOST_PORT))
                                print("control_mode = 0:青いボール追跡モード")
                            elif e.button == 5:
                                message = "Change_Mode:"+str(1)+":"+str(1)
                                publisher_sock.sendto(message, (PI_HOST_NAME , PI_HOST_PORT))
                                print("control_mode = 1:リモートコントロールモード")
            except Exception as e:
                print(str(e))

            #画像の取得待
            try:
                jpgstring, addr = receiver_sock.recvfrom(UBU_BUFF_SIZE)
                #string型からnumpyを用いuint8に戻す
                narray = numpy.fromstring(jpgstring, dtype = "uint8")
                #uint8のデータを画像データに戻す
                decimg = cv2.imdecode(narray,1)
                #画像の表示
                cv2.imshow(MAIN_WINDOW_NAME, decimg)
            except Exception as e:
                pass
            key = cv2.waitKey(WAIT_TIME)
            if key == 109 or key == 131149:  #m = 109, M 131149
                if control_mode == 1:         #0:青ボール追跡モード, 1:リモートコントロールモード
                    control_mode = 0
                    message = "Change_Mode:"+str(control_mode)+":"+str(control_mode)
                    publisher_sock.sendto(message, (PI_HOST_NAME , PI_HOST_PORT))
                    print("control_mode = 0:青いボール追跡モード")
                else:
                    control_mode = 1
                    message = "Change_Mode:"+str(control_mode)+":"+str(control_mode)
                    publisher_sock.sendto(message, (PI_HOST_NAME , PI_HOST_PORT))
                    print("control_mode = 1:リモートコントロールモード")

    except KeyboardInterrupt:         #Ctl+Cが押されたらループを終了
        print("Ctl+C\n")
    except Exception as e:
        print(str(e))
    finally:
        cv2.destroyAllWindows()
        #ラズパイでは少し待たないとウィンドウがクローズされない
        for i in range (1,10):
            cv2.waitKey(100)
        return


if __name__ == '__main__':
    main_loop()
    print("\nexit program")
