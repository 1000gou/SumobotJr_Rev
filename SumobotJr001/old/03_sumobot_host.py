#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import sys
import cv2
import numpy as np
import socket

############################################################################
#通信関連の定数
#PI_HOST_NAME = 'gapithree.local'    #ラズパイUDP受信ホスト名
PI_HOST_NAME = '192.168.2.200'    #ラズパイUDP受信ホスト名
PI_HOST_PORT = 4000                 #ラズパイUDP受信ポート番号
PI_BUFF_SIZE = 4096                 #ラズパイUDP受信バッファーサイズ
PI_SOKET_TIMEOUT = 0.001            #ラズパイUDPソケット待のタイムアウトまでの時間[s]
#UBU_HOST_NAME = 'gaubutwo.local'    #画像UDP受信ホスト名
UBU_HOST_NAME = '192.168.2.100'    #画像UDP受信ホスト名
UBU_HOST_PORT = 4001                #画像UDP受信ポート番号


#SumobotJrクラス関連の定数
MIN_SPEED = 10              #abs(設定速度)がMIN_SPEEDの場合は速度0に設定する
#GPIO_LEFT_SERVO = 12        #実際には左 12, 右　１３に接続しているが、
#GPIO_RIGHT_SERVO = 13       #音が出せないところではとりあえず、17,27にしてサーボを回さない
GPIO_LEFT_SERVO = 17
GPIO_RIGHT_SERVO = 27

#Ball detect クラス関連の定数
MAIN_WINDOW_NAME = "Image from Camera"
SUB_WINDOW_NAME = "Modified Image"
IMAGE_X = 320   #カメラから取得する画像のX（ターゲット値、なぜか実値はこの値にならない）
IMAGE_Y = 240   #カメラから取得する画像のY（ターゲット値、なぜか実値はこの値にならない）
MIN_SIZE_X = 20 #ターゲットの最小サイズX(ピクセル) : これ以下の矩形は無視
MIN_SIZE_Y = 20 #ターゲットの最小サイズY(ピクセル) ：　これ以下の矩形は無視
DETECT_COLOR = "blue"   #検出する色　赤:”red”, 青:"blue", 緑:"green" ,黄:"yellow"
#DETECT_COLOR = "green"   #検出する色　赤:”red”, 青:"blue", 緑:"green" ,黄:"yellow"
NO_TARGET = -999        #ターゲットがないときに返す数字（比率）

#メインループ内の定数
P_GAIN = 1              #目標追従性P_Gain（値が大きいと、回転軸側をの車輪が遅くなる）
SIZE_FORWARD = 30       #ターゲットが中心線からSIZE_FORWARD以内に入っているときは直進する
REDUCE_SEND_IMAGE = 10  #イメージ送信フレームの間引き
WAIT_TIME = 1                   #メインループの待ち時間（ms : これを入れないとウィンドウが表示されない）
PRINT_MAIN_LOOP_TIME = False     #メインループ１サイクルの時間を　True:表示する、False:表示しない

############################################################################
#GWS_35_STDをコントロールするためのクラス
class GWS_S35_STD_Class:
    # mPin : GPIO No (PWM)
    # mPwm : Pwmコントロール用のインスタンス
    # mReversal (1:CW/CCWそのまま、−１:CW/CCW反転)
    """コンストラクタ"""
    def __init__(self, Pin, Reversal):
        self.mPin = Pin
        self.mReversal = Reversal

        #車輪用GPIOをPWMモードにする
        GPIO.setup(self.mPin, GPIO.OUT)
        self.mPwm = GPIO.PWM(self.mPin , 500) # set 2.0ms / 500 Hz
        self.Stop()

    """停止"""
    def Stop(self):
        self.mPwm.start(0)

    """速度セット"""
    def SetSpeed(self, speed):
        if speed > 100:
            speed = 100
        elif speed < -100:
            speed = -100
        elif -MIN_SPEED < speed and speed < MIN_SPEED:
            self.Stop()
        else:
            #Duty ratio = ６０％〜９０％（1.2ms〜1.8ms)
            duty = (self.mReversal*speed+100)/200*30+60
            self.mPwm.start(duty)

    """終了処理"""
    def Cleanup(self):
        #PWMを0にしてから、インプットモードにしておく
        self.Stop()
        GPIO.setup(self.mPin, GPIO.IN)

############################################################################
#SumobotJrをコントロールするためのクラス
#各サーボは-100が後退方向、100が前進方向で指示する
class SumobotJr_Class:
    """コンストラクタ"""
    def __init__(self):
        #車輪用DCモーターコントローラーインスタンス作成
        try:
            #Useing GPIO No.  to idetify channel
            GPIO.setmode(GPIO.BCM)
            #左車輪用サーボ
            self.left_servo = GWS_S35_STD_Class(Pin = GPIO_LEFT_SERVO, Reversal=1)
            #右車輪用サーボ
            self.right_servo = GWS_S35_STD_Class(Pin = GPIO_RIGHT_SERVO, Reversal=-1)
            print("servo motor initialization succeeded")
        except Exception as e:
            self.no_problem = False
            print("DC motor initialaization error\n")
            print(str(e))

    """停止"""
    def Stop(self):
        self.left_servo.SetSpeed(0)
        self.right_servo.SetSpeed(0)

    """前進"""
    def Forward(self):
        self.left_servo.SetSpeed(100)
        self.right_servo.SetSpeed(100)

    """後退"""
    def Backward(self):
        self.left_servo.SetSpeed(-100)
        self.right_servo.SetSpeed(-100)

    """左折"""
    def Turn_left(self):
        self.left_servo.SetSpeed(-100)
        self.right_servo.SetSpeed(100)

    """右折"""
    def Turn_right(self):
        self.left_servo.SetSpeed(100)
        self.right_servo.SetSpeed(-100)

    """サーボの速度を直接設定する"""
    def SetSpeed(self, left, right):
        self.left_servo.SetSpeed(left)
        self.right_servo.SetSpeed(right)

    """終了処理"""
    def Cleanup(self):
        self.left_servo.Cleanup()
        self.right_servo.Cleanup()
        GPIO.cleanup()

###########################################################################
#Open CVベースのボール位置検出クラス
class Ball_detecter_Class:
    def __init__(self, size_x, size_y, flag_show_main_window, flag_show_sub_window):
        self.size_x = size_x
        self.size_y = size_y
        self.flag_show_main_window = flag_show_main_window
        self.flag_show_sub_window = flag_show_sub_window

        #Camera device initilization
        self.capture = cv2.VideoCapture(0)
        #Set target image size
        self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH , self.size_x)
        self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, self.size_y )
        #Get actual image size
        self.size_x = self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH )
        self.size_y =  self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

        #カメラディバイスが取得出来ない場合はエラーを投げる
        if self.capture.isOpened() is False:
            print('Camera device initialization error\n')
            raise('Camera device initialization error')
        else:
            print('Camera device initialization succeeded')
            print('Imaze size X:'+str(self.size_x)+'   Y:'+str(self.size_y) )

        #Windowの作成
        if self.flag_show_main_window:
            cv2.namedWindow(MAIN_WINDOW_NAME, cv2.WINDOW_AUTOSIZE)
        if self.flag_show_sub_window:
            cv2.namedWindow(SUB_WINDOW_NAME, cv2.WINDOW_AUTOSIZE)

        #一度だけイメージを読みこんでマスクを作成しておく
        flag, self.image = self.capture.read()
        self.mask = self.image
        if flag == False:
            print("Image can not be get from USB camera")

    def GetImage(self):
        flag, self.image = self.capture.read()
        if flag == False:
            print("Image can not be get from USB camera")

    #Open CVのHSV画像の説明
    #Hue(色相)→0~180(181～255の範囲は0からの循環に回される)
    #Saturation(彩度)→0~255
    #Value(明度)→0~255

    #青色の抽出
    def Extract_Blue(self, image):
        #青色の検出
        #lower = np.array([80, 100, 100])           #ボール全体を検出できるが誤検出が多い
        #upper = np.array([130, 255, 255])          #ボール全体を検出できるが誤検出が多い
        lower = np.array([100, 150, 100])
        upper = np.array([130, 255, 255])
        #lower = np.array([100, 180, 130])
        #upper = np.array([110, 255, 255])
        #lower = np.array([100, 200, 150])          #照明によってはボールが検出できない
        #upper = np.array([110, 255, 255])          #照明によってはボールが検出できない
        hsv = cv2.cvtColor(self.image,cv2.COLOR_BGR2HSV)
        return cv2.inRange(hsv,lower,upper)

    #赤色の抽出（誤検出が多いのでプログラムでは使っていない）
    def Extract_Red(self, image):
        # Redを検出
        lower = np.array([1, 150, 150])
        upper = np.array([10, 255, 255])
        hsv = cv2.cvtColor(self.image,cv2.COLOR_BGR2HSV)
        return cv2.inRange(hsv,lower,upper)
    #緑色を検出
    def Extract_Green(self, image):
        #lower = np.array([70, 150, 50])
        #upper = np.array([90, 255, 255])
        lower = np.array([70, 50, 50])
        upper = np.array([90, 255, 255])
        hsv = cv2.cvtColor(self.image,cv2.COLOR_BGR2HSV)
        return cv2.inRange(hsv,lower,upper)

    #黄色の抽出（誤検出が多いのでプログラムでは使っていない）
    def Extract_Yellow(self, image):
        # 黄色を検出
        lower = np.array([30, 20, 150])
        upper = np.array([70, 255, 255])
        hsv = cv2.cvtColor(self.image,cv2.COLOR_BGR2HSV)
        return cv2.inRange(hsv,lower,upper)

    #Windowをアップデートする
    #（ここではwaitをかけていないので、メインループでcv2.waitKey(WAIT_TIME)しないとウィンドウが表示されない）
    def UpdateWindow(self):
        if self.flag_show_main_window:
            cv2.imshow(MAIN_WINDOW_NAME, self.image)
        if self.flag_show_sub_window:
            cv2.imshow(SUB_WINDOW_NAME, self.mask)

    #検出した物体の重心を返す
    def Get_Rect_Position(self):
        self.GetImage()

        #DETECT_COLOR = 検出する色　赤:”red”, 青:"blue", 黄:"yellow"
        if DETECT_COLOR == "blue":
            #青色を抽出(2値化)
            self.mask = self.Extract_Blue(self.image)
        elif DETECT_COLOR == "red":
            #赤色を抽出（２値化）
            self.mask = self.Extract_Red(self.image)
        elif DETECT_COLOR == "green":
            #緑色を検出
            self.mask = self.Extract_Green(self.image)
        else :
            #黄色を抽出（２値化）
            self.mask = self.Extract_Yellow(self.image)

        #ノイズ除去
        self.mask = cv2.erode(self.mask, None, iterations=2)
        self.mask = cv2.dilate(self.mask, None, iterations=2)
        self.mask = cv2.GaussianBlur(self.mask , (33, 33), 3)

        #輪郭の取得
        contours, hierarchy = cv2.findContours(self.mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        #輪郭の表示（必要ない場合はコメントアウトしてもよい）
        cv2.drawContours(self.image,contours,-1,(0,0,255), thickness = 2)

        #輪郭からその物質を囲む矩形に変更
        rects = []
        for contour in contours:
            approx = cv2.convexHull(contour)
            rect = cv2.boundingRect(approx)
            rects.append(np.array(rect))

        #矩形がターゲットが見つかった場合は最大の矩形を選ぶ
        if len(rects) > 0:
            #最大矩形を取得
            pos_x, pos_y, size_x, size_y = max(rects, key=(lambda x: x[2] + x[3]))

            #矩形のサイズが極端に小さい場合は見つかっていないことにする
            #print("size_x:"+str(size_x))
            if size_x < MIN_SIZE_X or size_y < MIN_SIZE_Y:
                return NO_TARGET, NO_TARGET

            #矩形の描画
            cv2.rectangle(self.image, (pos_x,pos_y), (pos_x+size_x, pos_y+size_y), (0, 0, 255), thickness = 2)
            #矩形の中心を算出
            x = pos_x+size_x/2
            y = pos_y+size_y/2
            #ターゲットポイントを表示
            cv2.circle(self.image, (x, y), 5, (0, 0, 0), -1)
            #Windowを更新
            self.UpdateWindow()
            #ターゲットポイントを返す
            return x, y

        #ターゲットが見つからない場合
        else:
            #Windowを更新
            self.UpdateWindow()
            return NO_TARGET, NO_TARGET

    #青色の物体の中心地の座標率を返す
    #ratio_x : 画像左端-100、中央０、右端100を返す、物がない場合は-200を返す
    #ratio_y * 画面下端-100、中央０、上端100を返す、物がない場合は-200を返す。
    def Get_Rect_Position_Ratio(self):
        x, y = self.Get_Rect_Position()
        if x == NO_TARGET:
            return NO_TARGET,NO_TARGET
        else:
            #print("x:"+str(x))
            ratio_x = (float(x*200)/float(self.size_x))-100
            ratio_y = -((float(y*200)/float(self.size_y))-100)
            return ratio_x, ratio_y
    #後処理
    def Cleanup(self):
        self.capture.release()
        cv2.destroyAllWindows()
        #ラズパイでは少し待たないとウィンドウがクローズされない
        for i in range (1,10):
            cv2.waitKey(100)
###########################################################################
#メインループ
def main_loop():
    main_loop_flag = True       #Trueの間メインループを回す
    control_mode = 0            #0:青ボール追跡モード, 1:リモートコントロールモード
    skip_count_send_image = 0     #画像の送付を間引くための変数

    try:
        #SumobotJrクラスの初期化
        SumobotJr = SumobotJr_Class()

        #Ball_detecter_Class with OpenCV の初期化
        ball_detecter = Ball_detecter_Class(IMAGE_X,IMAGE_X, False, False)
        pre_x_ratio = NO_TARGET   #前回値をターゲット検出なしにしておく

        #UDP受信用ソケットの初期化
        #ソケットの初期化
        try:
            receiver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            receiver_sock.bind((PI_HOST_NAME, PI_HOST_PORT))
            receiver_sock.settimeout(PI_SOKET_TIMEOUT)
            cmd = ["NoCMD","0","0"]  #コマンドをNoCMDで初期化しておく
            print("controler　receiver soket initialaization succeeded")
        except Exception as e:
            print("controler　receiver soket initialaization error\n")
            print(str(e))
            main_loop_flag = False

        #ソケットの初期化（画像送信）
        try:
            publisher_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print("Image publisher soket initialaization succeeded")
        except Exception as e:
            print("Image publisher soket initialaization error\n")
            print(str(e))
            main_loop_flag = False

        #メインループ
        pre_time = time.time()
        while main_loop_flag:
            #受信用ソケットからコマンドを取得する。
            try:
                text = receiver_sock.recv(PI_BUFF_SIZE)
                cmd = text.split(":")
            except Exception as e:
                cmd = ["NoCMD","0","0"]

            #モード変更コマンド受信時
            if cmd[0] == "Change_Mode":
                control_mode = int(cmd[1])
                if control_mode == 0:
                    print("control_mode = 0:青いボール追跡モード")
                elif control_mode == 1:
                    SumobotJr.Stop()
                    print("control_mode = 1:リモートコントロールモード")

            #ボールを検出する
            x_ratio, y_ratio = ball_detecter.Get_Rect_Position_Ratio()
            #print("Ratio x:"+str(x_ratio)+"  y:"+str(y_ratio))
            #print("Pre_ratio x:"+str(pre_x_ratio))

            #ボール追跡モード
            if control_mode == 0:
                #ボールが見つからないときは前回値ベースでボールを探す。
                if x_ratio == NO_TARGET:
                    if pre_x_ratio < 0:
                        SumobotJr.Turn_left()
                    else:
                        SumobotJr.Turn_right()
                #ボールが画面の左端にある場合
                elif x_ratio < -SIZE_FORWARD:
                    pre_x_ratio = x_ratio
                    SumobotJr.SetSpeed(100-P_GAIN*abs(x_ratio),100)
                #ボールが画面の右端にある場合
                elif x_ratio > SIZE_FORWARD:
                    pre_x_ratio = x_ratio
                    SumobotJr.SetSpeed(100,100-P_GAIN*abs(x_ratio))
                #ボールが画面の中央付近にある場合はそのまま前進
                else:
                    SumobotJr.Forward()

            #リモート・コントロールモード
            elif control_mode == 1:
                if cmd[0] == 'left_right_stick':
                    SumobotJr.SetSpeed(float(cmd[1]),float(cmd[2]))
                    print("SetSpeed, left:"+cmd[1]+",right"+cmd[2])

            #画像送信
            #通信量が多くなるので画像の送信回数を間引く
            skip_count_send_image = skip_count_send_image+1
            if skip_count_send_image%REDUCE_SEND_IMAGE == REDUCE_SEND_IMAGE-1:
                skip_count_send_imag = 0
                #画像の送信
                #UDPで送る為に画像をstringに変換
                jpeg = cv2.cv.EncodeImage(".jpeg", cv2.cv.fromarray(ball_detecter.image))
                jpgstring = jpeg.tostring()
                try:
                    #画像の送信
                    publisher_sock.sendto(jpgstring, (UBU_HOST_NAME, UBU_HOST_PORT))
                except Exception as e:
                    print(str(e))
                #ループにかかった時間を表示
                if PRINT_MAIN_LOOP_TIME:
                    this_time = time.time()
                    print("１ループにかかった時間(%dループ平均):%.3f[s]"%(REDUCE_SEND_IMAGE,(this_time - pre_time)/REDUCE_SEND_IMAGE))
                    pre_time = this_time

            #メインループの待ち時間
            cv2.waitKey(WAIT_TIME)
    except KeyboardInterrupt  :         #Ctl+Cが押されたらループを終了
        print("\nCtl+C")
    except Exception as e:
        print(str(e))
    finally:
        SumobotJr.Cleanup()
        ball_detecter.Cleanup()

###########################################################################
if __name__ == '__main__':
    main_loop()
    print("\nexit program")
