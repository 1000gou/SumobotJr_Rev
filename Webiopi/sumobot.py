#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webiopi
import sys
import subprocess

GPIO = webiopi.GPIO

PIN_RIGHT = 13  #GPIOピンNo 右車輪
PIN_LEFT = 12   #GPIOピンNo 左車輪

"""イニシャライズ"""
def setup():
  #車輪用サーボをPWMモードにする
  GPIO.setFunction(PIN_RIGHT, GPIO.PWM)
  GPIO.setFunction(PIN_LEFT, GPIO.PWM)

"""終了処理"""
def destroy():
  #PWMを0にしてから、インプットモードにしておく
  GPIO.pulseMicro(PIN_RIGHT, 0, 2000)
  GPIO.setFunction(PIN_RIGHT, GPIO.INPUT)
  GPIO.pulseMicro(PIN_LEFT, 0, 2000)
  GPIO.setFunction(PIN_LEFT, GPIO.INPUT)

"""メインループ"""
def loop():
  webiopi.sleep(1)

"""停止"""
@webiopi.macro
def stop():
  right_up = 0
  left_up = 0
  GPIO.pulseMicro(PIN_RIGHT, right_up, 2000-right_up)
  GPIO.pulseMicro(PIN_LEFT, left_up, 2000-left_up)

"""前進"""
@webiopi.macro
def forward():
  right_up =  1100
  left_up = 1900
  GPIO.pulseMicro(PIN_RIGHT, right_up, 2000-right_up)
  GPIO.pulseMicro(PIN_LEFT, left_up, 2000-left_up)

"""後退"""
@webiopi.macro
def backward():
  right_up =  1900
  left_up = 1100
  GPIO.pulseMicro(PIN_RIGHT, right_up, 2000-right_up)
  GPIO.pulseMicro(PIN_LEFT, left_up, 2000-left_up)

"""右折"""
@webiopi.macro
def turn_right():
  right_up =  1900
  left_up = 1900
  GPIO.pulseMicro(PIN_RIGHT, right_up, 2000-right_up)
  GPIO.pulseMicro(PIN_LEFT, left_up, 2000-left_up)

"""左折"""
@webiopi.macro
def turn_left():
  right_up =  1100
  left_up = 1100
  GPIO.pulseMicro(PIN_RIGHT, right_up, 2000-right_up)
  GPIO.pulseMicro(PIN_LEFT, left_up, 2000-left_up)

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
