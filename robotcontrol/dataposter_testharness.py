import pandas as pd
from dataposter import DataPoster
from multiprocessing import Process, Pipe, Manager, Value


teachpoints = pd.read_excel('RobotPositions.xlsx',sheetname='Teachpoints')
sequences = pd.read_excel('RobotPositions.xlsx',sheetname='Sequences')
state = Manager().dict() #multiprocessing thread safe value passing
state['state'] = 'runSequence'

dp = DataPoster()
dp.initialize(teachpoints,sequences,state)

dp.postSequence(state['state'])
