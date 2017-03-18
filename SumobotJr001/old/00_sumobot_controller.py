#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import time
import pygame
from pygame.locals import *

############################################################################
#通信関連の定数
PI_HOST_NAME = 'gapithree.local'    #ラズパイUDP受信ホスト名
PI_HOST_PORT = 4000                 #ラズパイUDP受信ポート番号

def main_loop():
    main_loop_flag = True   #Trueの間メインループを回す

    #pygameの初期化
    try:
        pygame.joystick.init()
        joys = pygame.joystick.Joystick(0)
        joys.init()
        pygame.init()
        print("pygame initialaization succeeded")
    except Exception as e:
        print("pygame initialaization error\n")
        print(str(e))
        main_loop_flag = False

    #ソケットの初期化
    try:
        publisher_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("soket initialaization succeeded")
    except Exception as e:
        print("soket initialaization error\n")
        print(str(e))
        main_loop_flag = False

    try:
        while main_loop_flag:
            for e in pygame.event.get(): # イベントチェック
            #for e in pygame.event.pump(): # イベントチェック
                #print("getting event\n")
                if e.type == pygame.locals.JOYAXISMOTION: # 7
                    left_stick = -100*joys.get_axis(1)
                    right_stick = -100*joys.get_axis(4)
                    message = "left_right_stick:"+str(left_stick)+":"+str(right_stick)
                    publisher_sock.sendto(message, (PI_HOST_NAME , PI_HOST_PORT))

                elif e.type == pygame.locals.JOYBUTTONDOWN:
                    print(str(e.button)+'番目のボタンが押された')
                    if e.button == 4:
                        message = "Change_Mode:"+str(0)+":"+str(0)
                        publisher_sock.sendto(message, (PI_HOST_NAME , PI_HOST_PORT))
                        print("control_mode = 0:青いボール追跡モード")
                    elif e.button == 5:
                        message = "Change_Mode:"+str(1)+":"+str(1)
                        publisher_sock.sendto(message, (PI_HOST_NAME , PI_HOST_PORT))
                        print("control_mode = 1:リモートコントロールモード")

            time.sleep(0.01)
    except KeyboardInterrupt:         #Ctl+Cが押されたらループを終了
        print("Ctl+C\n")
    except Exception as e:
        print(str(e))
    finally:
        return


if __name__ == '__main__':
    main_loop()
    print("\nexit program")
