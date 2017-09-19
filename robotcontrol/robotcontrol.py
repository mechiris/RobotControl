from multiprocessing import Process, Pipe, Manager, Value
from Adafruit_PWM_Servo_Driver import PWM
from dataposter import DataPoster
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


    def goToTeachPoint(self,teachpoint,delay=1,steps=25):
        #this simply jerks then does a linear ramp over the move delay.  For longer moves, it is best practice to ramp at accel_max, move at vel_max, then decel.  The throw of the ROT2U is negligable for this, YMMV.
        incdelay = 1.0*delay/steps
        tp = self.teachpoints[self.teachpoints['Position'] == teachpoint]
        if tp.shape<1:
            logging.info('Teachpoint not found')
            return
        movesarr = np.zeros((6,steps)) 
        for channel,col in enumerate(tp.columns[2:]):
            position = tp.loc[tp.index[0],col]
            if ~pd.isnull(position):
                movesarr[channel] = np.linspace(self.servoPositions[channel],position,steps)
            else:
                movesarr[channel] = np.ones(steps) * self.servoPositions[channel] #dont move this servo
        movesarr = np.round(movesarr)
        for x in np.arange(0,steps):
            cur_positions = movesarr[:,x]
            for channel,value in enumerate(cur_positions):
                self.pwm.setPWM(channel,0,int(value))
                self.servoPositions[channel] = value
            time.sleep(incdelay)

    def goToServoPositionSmooth(self,channel,position,delay=1,steps=25):
        #this simply jerks then does a linear ramp over the move delay.  For longer moves, it is best practice to ramp at accel_max, move at vel_max, then decel.  The throw of the ROT2U is negligable for this, YMMV.
        incdelay = 1.0*delay/steps
        start_position = self.servoPositions[channel]
        inc_step = 1.0*(position - start_position)/steps
        new_pos = start_position

        while(True):
            arrived = False
            new_pos = int(new_pos + inc_step)
            
            if (start_position > position):
                if (new_pos<=position):
                    arrived = True
                    new_pos = position
            else:
                if (new_pos >= position):
                    arrived = True
                    new_pos = position
            self.pwm.setPWM(channel,0,new_pos)
            self.servoPositions[channel] = new_pos
            if arrived:
                break
            print('moved {}, sleeping for {}'.format(new_pos,incdelay))
            time.sleep(incdelay)
            
            


        self.pwm.setPWM(channel,0,position)
        self.servoPositions[channel] = position #update current log of positions


    def goToServoPosition(self,channel,position):
        self.pwm.setPWM(channel,0,position)
        self.servoPositions[channel] = position #update current log of positions
    
    def printCurrentServoPositions(self):
        for x,pos in enumerate(self.servoPositions):
            print(str(x)+ ": " + str(pos))
        self.changeState(0)


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

    # def goToTeachPoint(self,teachpoint,delay=0):
    #     tp = self.teachpoints[self.teachpoints['Position'] == teachpoint]
    #     if tp.shape<1:
    #         logging.info('Teachpoint not found')
    #         return
    #     for channel,col in enumerate(tp.columns[2:]):
    #         position = tp.loc[tp.index[0],col]
    #         if ~pd.isnull(position):
    #             self.goToServoPosition(int(channel),int(position))
    #     if delay>0:
    #         time.sleep(delay)
    
    def goToServoPositionMenu(self):
        servoextent = ''
        arrowDelta = 10 #delta to move when using arrow keys
        while (True):
            if servoextent == 'q':
                break;
            servoChannel = raw_input("Please input a servo channel (0-5).  Enter q to return to the main menu: ")
            if servoChannel == 'q':
                break;
            while(True):
                servoextent = raw_input("Please input a servo extent from 0 to 4096,  up or down arrows to nudge, or s to switch servo channel, q to return to the main menu")
                ## TODO: error input handling
                if servoextent == "s": 
                    logging.info('Switching channels')
                    break;
                elif servoextent == "q":
                    logging.info('Return to main menu')
                    break;
                elif servoextent == '\x1b[A': #up
                    self.goToServoPosition(int(servoChannel),int(self.servoPositions[int(servoChannel)]+arrowDelta))
                elif servoextent == '\x1b[B':
                    self.goToServoPosition(int(servoChannel),int(self.servoPositions[int(servoChannel)]-arrowDelta))
                else:
                    self.goToServoPosition(int(servoChannel), int(servoextent))
        self.changeState(0)
        
    def runSequence(self, sequence):
        try:
            cur_seq = sequences[sequences['sequence'] == sequence].iloc[0]
            pts = [str(p).strip() for p in cur_seq['teachpoints'].split(',')]
            delays = cur_seq['delays'].split(',')
        except:
            logging.info('No sequence ')
        if len(delays) != len(pts):
            logging.info('Delays array is a different length than teachpoints.  Generating delays')
            delays = np.arange()

        print('running sequence')
        if cur_seq['loop']:
            logging.info('Looping sequence.  Use CTL+C to exit loop')
        try:
            logging.info('Running sequence')
            while True:
                time.sleep(1)
                if not loop:
                    break;
        except KeyboardInterrupt:
            logging.info('Keypress detected, returning from sequence loop')
            pass

    
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
        try:
            states = {
            0 : 'mainMenu',
            1 : 'runSequence',
            2 : 'goToTeachPoint',
            3 : 'goToServoPosition',
            4 : 'printCurrentServoPositions',
            5 : 'shutdown',
            }  
            self.state['state'] = states[newState]

            options = {
            0 : self.mainMenu,
            1 : self.testSequence,
            2 : self.goToTeachPointMenu,
            3 : self.goToServoPositionMenu,
            4 : self.printCurrentServoPositions,
            5 : self.shutdown,
            }  
            options[newState]()
        except:
            print('Invalid option, returning to main menu')
            self.changeState(0)



    def mainMenu(self):
        print('\n\n\n')
        print('Main Menu:____________________________________________________________________________________')
        print('Please enter a number to select one of the following options:')
        print('1. Run Sequence')
        print('2. Go To TeachPoint')
        print('3. Go To Servo Position')
        print('4. List Current Servo Positions')
        print('5. Shutdown')
        newState = raw_input("Please input a number: ")
        self.changeState(int(newState))

    def __init__(self):
        #print('RobotControl Initializing')
        number_of_servos = 6

        if not os.path.exists('/var/log/robotcontrol'):
            os.makedirs('/var/log/robotcontrol')
        logging.basicConfig(filename='/var/log/robotcontrol/robotcontrol.log',level=logging.INFO)
        self.teachpoints = pd.read_excel('RobotPositions.xlsx',sheetname='Teachpoints')
        self.sequences = pd.read_excel('RobotPositions.xlsx',sheetname='Sequences')

        self.pwm = PWM(0x40) 
        self.servoPositions = self.teachpoints.loc[self.teachpoints['Position']=='safety'].iloc[:,2:].values[0]
        self.goToTeachPoint('safety')
        self.state = Manager().dict() #multiprocessing thread safe value passing
        self.state['state'] = 'Initializing'

