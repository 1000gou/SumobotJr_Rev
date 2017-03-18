#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import socket
import subprocess
import xml.etree.ElementTree as ET
import threading
import time
import pygame
from pygame.locals import *
import numpy

############################################################################
#通信関連の定数
#PI_HOST_NAME = 'gapithree.local'    #ラズパイUDP受信ホスト名
PI_HOST_NAME = '192.168.2.200'    #ラズパイUDP受信ホスト名
PI_HOST_PORT = 4000                 #ラズパイUDP受信ポート番号
#UBU_HOST_NAME = 'gaubutwo.local'    #画像UDP受信ホスト名
UBU_HOST_NAME = '192.168.2.100'    #画像UDP受信ホスト名
UBU_HOST_PORT = 4001                #画像UDP受信ポート番号
UBU_BUFF_SIZE = 1024*64             #画像UDP受信バッファーサイズ
UBU_SOKET_TIMEOUT = 0.01            #画像UDP受信タイムアウトまでの時間[s]
JULIUS_HOST_NAME = '127.0.0.1'      #Juliusサーバー(TCP)ホスト名
JULIUS_HOST_PORT = 10500            #Juliusサーバー(TCP)ポート番号
JULIUS_THREAD_SLEEP_TIME = 1        #Juliusスレッドの待ち時間
NO_COMMAND = "Nocommand"           #Juliusからのコマンドなし


#OpenCV関連の定数
MAIN_WINDOW_NAME = "Image from Raspberry pi"

#メインループ関連の
WAIT_TIME = 10                      #メインループの待ち時間（ms : これを入れないとウィンドウが更新されない）

############################################################################
# Julius（音声認識）をコントロールするクラス
class JuliusClientThreadClass(threading.Thread):
    def __init__(self, sleep_time):
        super(JuliusClientThreadClass, self).__init__()

        #スレッド関連のメンバ初期化
        self.lock = threading.Lock()
        self.sleep_time = sleep_time
        self.stop_event = threading.Event() #停止させるかのフラグ
        self.command = NO_COMMAND

        #Juliusの音声認識サーバーを起動する
        try:
            self.process = subprocess.Popen(["bash start_julius.sh"], stdout=subprocess.PIPE, shell=True)
            self.pid = self.process.stdout.read() # juliusのプロセスIDを取得
            print("Julius pid:"+str(self.pid))
            print("Julius server initialization succeeded")
        except Exception as e:
            print(str(e))
            print("Julius server initialization  error")
            #スレッドを停止させる
            self.stop()

        #TCPクライアントを作成し接続
        try:
            self.soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.soket.connect((JULIUS_HOST_NAME, JULIUS_HOST_PORT))
            print("Julius client initialization succeeded")
        except Exception as e:
            print(str(e))
            print("Julius client initialization  error")
            #スレッドを停止させる
            self.stop()

    def run(self):
        try:
            data = ""
            while not self.stop_event.is_set():
                if "</RECOGOUT>\n." in data:
                    #変数変更前withを使ってスレッドをロックする
                    with self.lock:
                        # RECOGOUT要素以下をXMLとしてパース
                        tmp = '<?xml version="1.0"?>\n' + data[data.find("<RECOGOUT>"):data.find("</RECOGOUT>")+11]
                        root = ET.fromstring(tmp)
                        # 言葉を判別
                        for whypo in root.findall("./SHYPO/WHYPO"):
                            self.command = whypo.get("WORD")
                            #print("sub_loop:"+self.command)
                        data = ""
                else:
                    data = data + self.soket.recv(1024)
                time.sleep(self.sleep_time)
        except Exception as e:
            print(str(e))
        finally:
            self.Cleanup()

    #スレッドを停止させる
    def stop(self):
        self.stop_event.set()
        self.join()             #スレッドが停止するのを待つ

    #終了準備
    def Cleanup(self):
        #Juliusの音声認識サーバーを終了する
        subprocess.call(["kill " + self.pid], shell=True)
        #TCPクライアントを終了する
        self.soket.close()
        print("JuliusClientThreadClass:cleaned up")

########################################################################
#メインループ
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

    #Juliusの初期化
    try:
        JuliusThread = JuliusClientThreadClass(JULIUS_THREAD_SLEEP_TIME)
        JuliusThread.start()
        time.sleep(0.1)
    except Exception as e:
        print(str(e))
        main_loop_flag = False
    
    try:
        while main_loop_flag:
            #ジョイスティックイベント処理
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
                
            #Julius(音声コマンド処理)
            try:
                if JuliusThread.command != NO_COMMAND:
                    #変数変更前withを使ってスレッドをロックする
                    with JuliusThread.lock:
                        command = JuliusThread.command
                        JuliusThread.command = NO_COMMAND
                    if control_mode == 1:   #control_mode = 1:リモートコントロールモード
                        if command == "左".encode():
                            message = "left_right_stick:"+str(100)+":"+str(-100)
                            publisher_sock.sendto(message, (PI_HOST_NAME , PI_HOST_PORT))
                            print("音声コマンド:右")
                        elif command == "left":
                            message = "left_right_stick:"+str(-100)+":"+str(100)
                            publisher_sock.sendto(message, (PI_HOST_NAME , PI_HOST_PORT))
                            print("音声コマンド:左")
                        elif command == "left":
                            message = "left_right_stick:"+str(100)+":"+str(100)
                            publisher_sock.sendto(message, (PI_HOST_NAME , PI_HOST_PORT))
                            print("音声コマンド:前進")
                        elif command == "left":
                            message = "left_right_stick:"+str(-100)+":"+str(-100)
                            publisher_sock.sendto(message, (PI_HOST_NAME , PI_HOST_PORT))
                            print("音声コマンド:前進")
                        else:
                            message = "left_right_stick:"+str(0)+":"+str(0)
                            publisher_sock.sendto(message, (PI_HOST_NAME , PI_HOST_PORT))
                            print("音声コマンド:止まれ")
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

            #キーボードからの入力待
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
        JuliusThread.stop()
        cv2.destroyAllWindows()
        #ラズパイでは少し待たないとウィンドウがクローズされない
        for i in range (1,10):
            cv2.waitKey(100)
        return


if __name__ == '__main__':
    main_loop()
    print("\nexit program")
