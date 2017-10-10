import pandas as pd
from dataposter import DataPoster
from multiprocessing import Process, Pipe, Manager, Value
import os

teachpoints = pd.read_csv('Teachpoints.csv')
sequences = pd.read_csv('Sequences.csv',delimiter=';')
state = Manager().dict() #multiprocessing thread safe value passing
state['state'] = 'runSequence'

directory = '/opt/sightmachine/data/robotdata/'
if not os.path.exists(directory):
    os.makedirs(directory)


dp = DataPoster()
dp.initialize(teachpoints,sequences,state)

dp.postSequence(state['state'])
