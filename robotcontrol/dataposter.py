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

    def generateTrajectory(self, sequence):
        trajectory = pd.DataFrame(columns=self.teachpoints.columns)
        cur_seq = self.sequences[self.sequences['sequence'] == sequence].iloc[0]
        
        pts = [str(p).strip() for p in cur_seq['teachpoints'].split(',')]
        delays = cur_seq['delays'].split(',')

        for x,p in enumerate(pts): 
            tp = self.teachpoints[self.teachpoints['Position'] == p].iloc[0]
            tp['delay']= delays[x]
            trajectory = trajectory.append(tp)
        trajectory.index = np.arange(0,trajectory.shape[0])
        trajectory = trajectory.fillna(method='pad')
        fulltrajectory = self.interpolateFullTrajectory(trajectory)
        return fulltrajectory

    def interpolateFullTrajectory(self,trajectory, pollrate = 0.1):
        fulltrajectory = pd.DataFrame(columns=list(self.teachpoints.columns) + ['Time'])
        cur_time = 0
        for x,row in enumerate(trajectory.iterrows()):
            if x >= trajectory.shape[0]-1:
                nextrow = trajectory.iloc[0]
            else:
                nextrow = trajectory.iloc[x+1]
            cur_move = pd.DataFrame(columns=fulltrajectory.columns)
            cur_move['Time'] = np.arange(cur_time,cur_time+float(row[1]['delay']),pollrate)
            for col in row[1].keys()[2:]:
                cur_move[col] = np.linspace(row[1][col],nextrow[col],cur_move.shape[0])

            cur_move['Position'] = row[1]['Position']
            cur_move.loc[0,'Position':'s5']= row[1]
            fulltrajectory = fulltrajectory.append(cur_move)
            cur_time += float(row[1]['delay'])
            #cur_move[.iloc[0]
        fulltrajectory.index = np.arange(0,fulltrajectory.shape[0])
        fulltrajectory['counter'] = self.counter 
        return fulltrajectory


    def saveTrajectory(self,fulltrajectory,path='/opt/sightmachine/data/robotdata/'):
        outfile = path+time.strftime("%Y%m%d-%H%M%S") + '.csv'
        fulltrajectory.to_csv(outfile)
        sleeptime = fulltrajectory['Time'].iloc[-1] - fulltrajectory['Time'].iloc[0]
        print('Saving {}s trajectory to: {}'.format(sleeptime,outfile))
        time.sleep(sleeptime)

    def postSequence(self, initstate, sequence='Pick_Place_cups'):
        if not sequence in self.trajectories:
            logging.info('Trajectory not found, generating')
            self.trajectories[sequence] = self.generateTrajectory(sequence)

        while(True):
            cur_trajectory = self.trajectories[sequence].copy()
            ## add noise
            cur_trajectory = self.addNoise(cur_trajectory)
            cur_trajectory['counter'] = self.counter 
            cur_trajectory['timestamp'] = 0
            for x in np.arange(0,cur_trajectory.shape[0]):
                cur_trajectory.loc[x,'timestamp'] = datetime.datetime.utcnow() + datetime.timedelta(0,cur_trajectory.loc[x,'Time'])
#                cur_trajectory['timestamp'].iloc[x] = datetime.datetime.utcnow() + datetime.timedelta(0,cur_trajectory['Time'].iloc[x])
            self.saveTrajectory(cur_trajectory)            
            if self.state['state'] != initstate:
                break;
            self.counter += 1
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
            print('holdingPattern')
            time.sleep(1)
            if self.state['state'] != initstate:
                break;
        self.changeState()

    def addNoise(self,fulltrajectory):
        #adds noise to a dataframe with servo trajectory values
        for x,row in enumerate(fulltrajectory.iterrows()):
            row[1][2:-2] *= 1+np.random.rand()/100
            fulltrajectory.loc[x,2:-2] = row[1][2:-2]
        return fulltrajectory

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
            self.holdingPattern(self.state['state']) #wait for another state change
    
    def initialize(self,teachpoints,sequences,state):
        self.teachpoints = teachpoints
        self.sequences = sequences
        self.state = state
        self.trajectories = {} #dict of trajectories to save for sslog collection
        self.keySequence = ''

    def __init__(self):
        ### Configureable parameters ###
        # Breathing Motion
        print('created poster class') 
        self.counter = 0
