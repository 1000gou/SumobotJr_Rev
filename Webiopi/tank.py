#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webiopi
import sys
import subprocess

GPIO = webiopi.GPIO

Left_pin_ref=17     #GPIO No 左PWM
Left_pin_out1=18    #GPIO No 左out1
Left_pin_out2=27    #GPIO No 左out2

Right_pin_ref=22    #GPIO No 右PWM
Right_pin_out1=23   #GPIO No 右out1
Right_pin_out2=24   #GPIO No 右out2

"""イニシャライズ"""
def setup():
    #左車輪
    GPIO.setFunction(Left_pin_ref, GPIO.PWM)
    GPIO.setFunction(Left_pin_out1, GPIO.OUT)
    GPIO.setFunction(Left_pin_out2, GPIO.OUT)

    #右車輪
    GPIO.setFunction(Right_pin_ref, GPIO.PWM)
    GPIO.setFunction(Right_pin_out1, GPIO.OUT)
    GPIO.setFunction(Right_pin_out2, GPIO.OUT)

"""停止"""
@webiopi.macro
def stop():
    #左車輪
    GPIO.pwmWrite(Left_pin_ref,100)
    GPIO.digitalWrite(Left_pin_out1, GPIO.LOW)
    GPIO.digitalWrite(Left_pin_out2, GPIO.LOW)

    #右車輪
    GPIO.pwmWrite(Left_pin_ref,100)
    GPIO.digitalWrite(Right_pin_out1, GPIO.LOW)
    GPIO.digitalWrite(Right_pin_out2, GPIO.LOW)

"""前進"""
@webiopi.macro
def forward():
    #左車輪
    GPIO.pwmWrite(Left_pin_ref,100)
    GPIO.digitalWrite(Left_pin_out1, GPIO.HIGH)
    GPIO.digitalWrite(Left_pin_out2, GPIO.LOW)

    #右車輪
    GPIO.pwmWrite(Left_pin_ref,100)
    GPIO.digitalWrite(Right_pin_out1, GPIO.HIGH)
    GPIO.digitalWrite(Right_pin_out2, GPIO.LOW)

"""後退"""
@webiopi.macro
def backward():
    #左車輪
    GPIO.pwmWrite(Left_pin_ref,100)
    GPIO.digitalWrite(Left_pin_out1, GPIO.LOW)
    GPIO.digitalWrite(Left_pin_out2, GPIO.HIGH)

    #右車輪
    GPIO.pwmWrite(Left_pin_ref,100)
    GPIO.digitalWrite(Right_pin_out1, GPIO.LOW)
    GPIO.digitalWrite(Right_pin_out2, GPIO.HIGH)

"""左折"""
@webiopi.macro
def turn_left():
    #左車輪
    GPIO.pwmWrite(Left_pin_ref,100)
    GPIO.digitalWrite(Left_pin_out1, GPIO.HIGH)
    GPIO.digitalWrite(Left_pin_out2, GPIO.LOW)

    #右車輪
    GPIO.pwmWrite(Left_pin_ref,100)
    GPIO.digitalWrite(Right_pin_out1, GPIO.LOW)
    GPIO.digitalWrite(Right_pin_out2, GPIO.HIGH)

"""右折"""
@webiopi.macro
def turn_right():
    #左車輪
    GPIO.pwmWrite(Left_pin_ref,100)
    GPIO.digitalWrite(Left_pin_out1, GPIO.LOW)
    GPIO.digitalWrite(Left_pin_out2, GPIO.HIGH)

    #右車輪
    GPIO.pwmWrite(Left_pin_ref,100)
    GPIO.digitalWrite(Right_pin_out1, GPIO.HIGH)
    GPIO.digitalWrite(Right_pin_out2, GPIO.LOW)

"""ラズパイ終了"""
@webiopi.macro
def raspberry_pi_halt():
    cmd = "sudo halt"
    subprocess.call(cmd,  shell=True)

"""mjpg_streamer スタート"""
@webiopi.macro
def mjpg_streamer_start():
    cmd = "sudo /home/pi/mjpg-streamer/mjpg_streamer -i \"/home/pi/mjpg-streamer/input_uvc.so -f 10 -r 320x240 -d /dev/video0 -y -n\" -o \"/home/pi/mjpg-streamer/output_http.so -w /home/pi/mjpg-streamer/www -p 8080\" &"
    subprocess.call(cmd,  shell=True)
