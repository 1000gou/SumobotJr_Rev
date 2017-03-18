#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import sys
import cv2
import numpy as np

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
        elif -10 < speed and speed < 10:
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
class SumobotJr_Class:
    """コンストラクタ"""
    def __init__(self):
        #車輪用DCモーターコントローラーインスタンス作成
        try:
            #Useing GPIO No.  to idetify channel
            GPIO.setmode(GPIO.BCM)
            self.left_servo = GWS_S35_STD_Class(Pin = 12, Reversal=1)       #左車輪用サーボ
            self.right_servo = GWS_S35_STD_Class(Pin = 13, Reversal=-1)     #右車輪用サーボ
            self.no_problem = True                                          #クラスの中で問題が起きていないか(True:問題なし)
            print("servo motor initialaization is succeeded")
        except Exception as e:
            self.no_problem = False
            print("DC motor initialaization error")
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

    """終了処理"""
    def Cleanup(self):
        self.left_servo.Cleanup()
        self.right_servo.Cleanup()
        GPIO.cleanup()

if __name__ == '__main__':
    SumotoJr = SumobotJr_Class()
    try:
        while True:
            SumotoJr.Forward()
            time.sleep(1)
            SumotoJr.Backward()
            time.sleep(1)
            SumotoJr.Turn_left()
            time.sleep(1)
            SumotoJr.Turn_right()
            time.sleep(1)
            SumotoJr.Stop()
            time.sleep(1)
    except KeyboardInterrupt  :         #Ctl+Cが押されたらループを終了
        print("\nCtl+C")
    except Exception as e:
        print(str(e))
    finally:
        SumotoJr.Cleanup()
        print("\nexit program")
