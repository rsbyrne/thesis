import sys
import os

thesisdir = os.path.dirname(os.path.abspath(__file__))
resourcesdir = os.path.join(thesisdir, 'resources')
datadir = os.path.join(thesisdir, 'data')
cachedir = os.path.join(thesisdir, 'cache')
# utilitiesdir = os.path.join(thesisdir, 'utilities')
analysisdir = os.path.join(thesisdir, 'analysis')
bookdir = os.path.join(thesisdir, 'book')
productsdir = os.path.join(thesisdir, 'products')
scratchdir = os.path.join(thesisdir, 'scratch')
storagedir = os.path.join(thesisdir, 'storage')
referencesdir = os.path.join(bookdir, 'main')
everestdir = os.path.join(resourcesdir, 'everest')

# if not utilitiesdir in sys.path:
#     sys.path.insert(0, utilitiesdir)
if not resourcesdir in sys.path:
    sys.path.insert(0, resourcesdir)

import pickle
from pathlib import Path

import pandas as pd
import scipy as sp
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
import numpy as np
import math

from everest.window import Canvas, DataChannel as Channel
import utilities

import analysis