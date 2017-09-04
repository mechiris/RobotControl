from multiprocessing import Process, Pipe, Manager, Value
from Adafruit_PWM_Servo_Driver import PWM
fromt dataposter import DataPoster
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
        self.pwm.setPWM(channel, 0, pulse)

    def dataPoster(self, state):
        print('TODO: Flesh this out')

    def start(self):
        logging.info('Run started')

        # self.dataPoster = DataPoster()
        # self.dataPoster.Initialize(self.teachpoints,self.sequences,self.state)
        # self.parent_conn, self.child_conn = Pipe()
        # p = Process(target=self.dp.changeState)
        # p.start()

        self.mainMenu()

        # p.join()

    def goToServoPosition(self,channel,position):
        self.pwm.setPWM(channel,0,position)

    
    def goToTeachPointMenu(self):
        while (True):
            print('\n')
            teachPoint = raw_input("Please input a teachpoint to go to.  Enter l to list available teachpoints, q to return to the main menu: ")
            if teachPoint == 'l':
                for pos in self.teachpoints['Position'].unique():
                    print(pos)
            elif teachPoint == 'q':
                break;
            else:
                self.goToTeachPoint(teachPoint)
        self.changeState(0)

    def goToTeachPoint(self,teachpoint,delay=0):
        tp = self.teachpoints[self.teachpoints['Position'] == teachpoint]
        if tp.shape<1:
            logging.info('Teachpoint not found')
            return
        for channel,col in enumerate(tp.columns[2:]):
            position = tp.loc[tp.index[0],col]
            if ~pd.isnull(position):
                self.goToServoPosition(int(channel),int(position))
        if delay>0:
            time.sleep(delay)
    
    def goToServoPositionMenu(self):
        servoextent = ''
        while (True):
            if servoextent == 'q':
                break;
            servoChannel = raw_input("Please input a servo channel (0-5).  Enter q to return to the main menu: ")
            if servoChannel == 'q':
                break;
            while(True):
                servoextent = raw_input("Please input a servo extent from 0 to 4096, or s to switch servo channel, q to return to the main menu")
                if servoextent == "s":
                    logging.info('Switching channels')
                    break;
                if servoextent == "q":
                    logging.info('Return to main menu')
                    break;
                else:
                    self.pwm.setPWM(int(servoChannel), 0, int(servoextent))
        self.changeState(0)
        
    def runSequence(self):
        print('running sequence')

        pts = [str(p).strip() for p in pts]
    
    def shutdown(self):
        logging.info('Shutting down system')
        self.goToTeachPoint('safety')
        time.sleep(0.5)
        self.goToTeachPoint('rest')

    def testSequence(self):
        while(True):
            self.goToTeachPoint('safety')
            time.sleep(1)
            self.goToTeachPoint('left_pick_hover')
            time.sleep(1)
            self.goToTeachPoint('left_pick')
            time.sleep(1)
            self.goToTeachPoint('grip_closed')
            time.sleep(1)
            self.goToTeachPoint('left_pick_hover')
            time.sleep(1)
            self.goToTeachPoint('safety')
            time.sleep(1)
            self.goToTeachPoint('right_pick_hover')
            time.sleep(1)
            self.goToTeachPoint('grip_open')
            time.sleep(1)
            self.goToTeachPoint('right_pick')
            time.sleep(1)
            self.goToTeachPoint('grip_closed')
            time.sleep(1)
            self.goToTeachPoint('right_pick_hover')
            time.sleep(1)

    def changeState(self, newState):
        states = {
        0 : 'mainMenu',
        1 : 'runSequence',
        2 : 'goToTeachPoint',
        3 : 'goToServoPosition',
        4 : 'shutdown',
        }  
        self.state['state'] = states[newState]

        options = {
        0 : self.mainMenu,
        1 : self.runSequence,
        2 : self.goToTeachPointMenu,
        3 : self.goToServoPositionMenu,
        4 : self.shutdown,
        }  
        options[newState]()



    def mainMenu(self):
        print('\n\n\n')
        print('Main Menu:____________________________________________________________________________________')
        print('Please enter a number to select one of the following options:')
        print('1. Run Sequence')
        print('2. Go To TeachPoint')
        print('3. Go To Servo Position')
        print('4. Shutdown')
        newState = raw_input("Please input a number: ")
        self.changeState(int(newState))
        #runSequence
        #goToTeachPoint
        #goToServoPosition
        #shutdown

    def __init__(self):
        #print('RobotControl Initializing')
        if not os.path.exists('/var/log/robotcontrol'):
            os.makedirs('/var/log/robotcontrol')
        logging.basicConfig(filename='/var/log/robotcontrol/robotcontrol.log',level=logging.INFO)
        self.teachpoints = pd.read_excel('RobotPositions.xlsx',sheetname='Teachpoints')
        self.sequences = pd.read_excel('RobotPositions.xlsx',sheetname='Sequences')

        self.pwm = PWM(0x40) 
        self.goToTeachPoint('safety')
        self.state = Manager().dict() #multiprocessing thread safe value passing
        self.state['state'] = 'Initializing'

