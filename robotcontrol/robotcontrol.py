from multiprocessing import Process, Pipe, Value
from Adafruit_PWM_Servo_Driver import PWM
import RPi.GPIO as GPIO
import datetime, time
import pandas as pd
import numpy as np
import subprocess as sbp
import logging
import os
import glob
import json
import csv
import copy 


class RobotControl():
    def setServoPulse(self,channel, pulse):
        pulseLength = 1000000                   # 1,000,000 us per second
        pulseLength /= 60                       # 60 Hz
        pulseLength /= 4096                     # 12 bits of resolution
        pulse *= 1000
        pulse /= pulseLength
        pwm.setPWM(channel, 0, pulse)

    def RunMotor(self,counter, runMotor):
        #Initialise the PWM device using the default address
        pwm = PWM(0x40) #for debug: pwm = PWM(0x40, debug=True)

        logging.info('Initializing servo motion')
        with counter.get_lock():
            counter.value =0
        while(runMotor.value):
            pwm.setPWM(0, 0, self.servoMin)
            time.sleep(self.breathTime)
            pwm.setPWM(0, 0, self.servoMax)
            time.sleep(self.breathTime)
            with counter.get_lock():
                counter.value += 1
            logging.info('Stopping motor')
        pwm.setPWM(0,0,self.servoSlack)

    def start(self):
        logging.info('Run started')
        self.userInputSingleServoPosition()

    def goToServoPosition(self,channel,position):
        self.pwm.setPWM(channel,0,position)
    
    def userInputSingleServoPosition(self):
        while (True):
            servoChannel = raw_input("Please input a servo channel (0-5).  Enter q to stop: ")
            if servoChannel == 'q':
                break;
            while(True):
                servoextent = raw_input("Please input a servo extent from 0 to 4096, or s to switch servo channel")
                if servoextent == "s":
                    logging.info('Switching channels')
                    break;
                else:
                    pwm.setPWM(servoChannel, 0, int(servoextent))
        


    def __init__(self):
        print('RobotControl Initialized')

        self.pwm = PWM(0x40) #for debug: pwm = PWM(0x40, debug=True)
        #self.start()
        self.state = Value('d', -1) #multiprocessing thread safe value passing

        if not os.path.exists('/var/log/robotcontrol'):
            os.makedirs('/var/log/robotcontrol')
        logging.basicConfig(filename='/var/log/autopump/robotcontrol.log',level=logging.INFO)