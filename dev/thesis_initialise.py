import sys, os

workDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
resourcesDir = os.path.join(workDir, 'resources')
dataDir = os.path.join(workDir, 'data')

if not resourcesDir in sys.path:
    sys.path.insert(0, resourcesDir)

everestDir = os.path.join(resourcesDir, 'everest')
if not everestDir in sys.path:
    sys.path.insert(0, everestDir)

import numpy as np
import scipy as sp
import dask
from dask import (
    array as da,
    dataframe as dd,
    bag as db
    )
import h5py

# from everest.funcy import Fn
