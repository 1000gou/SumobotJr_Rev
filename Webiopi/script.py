#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webiopi

GPIO = webiopi.GPIO

LIGHT = 4 # GPIO pin using BCM numbering


# setup function is automatically called at WebIOPi startup
def setup():
    # set the GPIO used by the light to output
    GPIO.setFunction(LIGHT, GPIO.OUT)

# loop function is repeatedly called by WebIOPi
def loop():
    # retrieve current datetime
    now = datetime.datetime.now()

    # toggle light ON
    if (GPIO.digitalRead(LIGHT) == GPIO.LOW):
        GPIO.digitalWrite(LIGHT, GPIO.HIGH)

    # toggle light OFF
    if (GPIO.digitalRead(LIGHT) == GPIO.HIGH):
        GPIO.digitalWrite(LIGHT, GPIO.LOW)

    # gives CPU some time before looping again
    webiopi.sleep(1)

# destroy function is called at WebIOPi shutdown
def destroy():
    GPIO.digitalWrite(LIGHT, GPIO.LOW)
