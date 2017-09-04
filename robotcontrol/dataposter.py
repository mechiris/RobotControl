from multiprocessing import Process, Pipe, Manager, Value
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

class DataPoster():
    def postSequence(self, initstate):
        while(True):
            print('Posting sequence')
            if self.state['state'] != initstate:
                break;
            time.sleep(1)
        self.changeState()

    def postStopped(self,initstate):
        while(True):
            print('Posting stopped')
            if self.state['state'] != initstate:
                break;
            time.sleep(1)
        self.changeState()

    def holdingPattern(self,initstate):
        while(True):
            print('holdingPatter')
            time.sleep(1)
            if self.state['state'] != initstate:
                break;
        self.changeState()

    def shutdown(self):
        print('Shutting down')
        return

    def changeState(self):
        options = {
        'mainMenu' : self.postStopped,
        'runSequence' : self.postSequence,
        'goToTeachPoint' : None,
        'goToServoPosition' : None,
        'shutdown' : self.shutdown,
        }
        newState = options[self.state['state']]
        if newState:
            newState(self.state['state'])
        else:
            self.holdingPattern(self.state['state'])
    
    def initialize(self,teachpoints,sequences,state):
        self.teachpoints = teachpoints
        self.sequences = sequences
        self.state = state

    def __init__(self):
        ### Configureable parameters ###
        # Breathing Motion
        print('created poster class') 
