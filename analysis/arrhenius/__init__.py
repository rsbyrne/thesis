from .. import *

import pickle
import os

dirpath = os.path.dirname(__file__)

path = os.path.join(dirpath, 'arrRa7inputs.pkl')
try:
    with open(path, mode = 'rb') as file:
        arrRa7inputs = pickle.loads(file.read())
except FileNotFoundError:
    arrRa7inputs = arrinputs.loc[arrinputs['alpha'] == 7].loc[arrinputs['etaDelta'] == 3e4]
    with open(path, mode = 'wb') as file:
        file.write(pickle.dumps(arrRa7inputs))

path = os.path.join(dirpath, 'arrRa7list.pkl')
try:
    with open(path, mode = 'rb') as file:
        arrRa7list = pickle.loads(file.read())
except FileNotFoundError:
    arrRa7list = list(arrRa7inputs.index)
    with open(path, mode = 'wb') as file:
        file.write(pickle.dumps(arrRa7list))
