from thesis_initialise import *

from merge import *

import pickle
import os

dirpath = os.path.dirname(__file__)

inputframespath = os.path.join(dirpath, 'inputframes.pkl')
try:
    with open(inputframespath, mode = 'rb') as file:
        isoinputs, arrinputs, plastinputs = pickle.loads(file.read())
except FileNotFoundError:
    isoinputs, arrinputs, plastinputs = inputframes = tuple(
        make_frame(get_inputs()[key])
            for key in {'Isovisc', 'Arrhenius', 'Viscoplastic'}
        )
    with open(inputframespath, mode = 'wb') as file:
        file.write(pickle.dumps(inputframes))